# Go service rewrite — implementation plan

Status: **accepted, not yet started**
Tracking issue: [#34](https://github.com/dustfeather/device-activity-telegram-bot/issues/34)
Date: 2026-09-11

Scope of this document: the decisions that are settled, the evidence behind them,
and what is still open. It supersedes the parts of #34 that research has since
contradicted — those are called out explicitly under [Corrections to #34](#corrections-to-34).

---

## 1. Summary

Rewrite the bot as a single statically-linked Go binary that installs itself as a
native OS service, replacing the Python app wired to Task Scheduler and cron.

The binary is one long-running service per machine. It handles **both** responsibilities
that 1.x split across two entrypoints:

- the login/unlock notification (`send.py` today), and
- the Telegram long-poll loop serving `/halt` (`halt.py` today).

There is no separate one-shot process and no scheduled task. `send` as a distinct
entrypoint does not survive the rewrite.

---

## 2. Decisions

### D1 — Clean replacement on `main`; Python preserved by tag and branch

`main` becomes pure Go. `src/`, `tests/`, `send.spec`, `setup.py` and the PyInstaller
requirements are deleted as part of the rewrite.

Before the first Go commit:

1. tag `v1.0.0` at the current Python HEAD,
2. cut `maint/1.x` from that tag.

The repo has **no tags today**, so "keep 1.x on a maintenance branch" (as #34 phrases it)
has nothing to cut from until this happens. The tag must include the `/halt` authorization
fix (see [D6](#d6--sender-authorization-is-an-invariant)) so the preserved Python line is
not the vulnerable one.

Rejected: side-by-side Python and Go on `main` (two CI matrices, two dependency bots, two
lint configs for ~260 LOC), and a separate repository (loses issue and CI history; #34 asks
for a rewrite, not a new project).

### D2 — Windows drops to `x/sys/windows/svc`; `kardianos/service` elsewhere

`github.com/kardianos/service` handles install/uninstall/run on Linux. On Windows the
service run loop is written directly against `golang.org/x/sys/windows/svc` so it can
advertise `svc.AcceptSessionChange`.

**Why, with evidence.** #34 assumed one library covered the whole service story. It does
not. `kardianos/service` v1.3.0 hardcodes the accepted-control mask:

```
service_windows.go:182:  const cmdsAccepted = svc.AcceptStop | svc.AcceptShutdown
```

and the module contains **zero** references to `WTS`, `SessionChange`, `AcceptSessionChange`
or `SessionLogon`. On Windows a service receives a control code only if it advertised
acceptance of it in the `SERVICE_STATUS` it reports to the SCM, so
`SERVICE_CONTROL_SESSIONCHANGE` — carrying `WTS_SESSION_LOGON` and `WTS_SESSION_UNLOCK` —
never arrives. Nothing errors; the handler is simply never called.

The limitation is the wrapper's, not Windows' and not `x/sys`': `golang.org/x/sys/windows/svc`
exposes `svc.AcceptSessionChange` and delivers the change requests. There is no exported
option to widen the mask, so the only way to get logon/unlock is to run the SCM loop directly.

Cost accepted: the service abstraction forks on exactly one platform.

Rejected: registering a separate logon-triggered scheduled task (covers logon but not
unlock — unlock needs `/sc ONEVENT` on Security log 4801 — and a console-subsystem binary
launched by a logon task flashes a console window); polling session state on a timer.

### D3 — Targets: `windows/amd64`, `linux/amd64`, `linux/arm64`. No macOS.

Full session parity (logon **and** unlock) on both shipped platforms:

- **Windows** — `x/sys/windows/svc` with `AcceptSessionChange`, per D2.
- **Linux** — systemd-logind over D-Bus (`org.freedesktop.login1`): `SessionNew` for login,
  the session `Lock`/`Unlock` signals for lock state. `github.com/godbus/dbus/v5` is pure Go
  — its only `import "C"` is `transport_unixcred_dragonfly.go`, which is never built on
  these targets. Verified by clean `CGO_ENABLED=0` cross-builds for linux/arm64,
  windows/amd64 and darwin/arm64.

macOS is dropped from 2.0. Login there is free (a launchd agent with `RunAtLoad`), but
unlock requires `com.apple.screenIsUnlocked` from `NSDistributedNotificationCenter` — Obj-C,
therefore cgo, which breaks `CGO_ENABLED=0` on that target and means the darwin binary can
no longer be cross-compiled from Linux. That reintroduces the per-target-builder problem
that got .NET rejected in #34. There is no macOS requirements file in the repo and no other
evidence a Mac is in use.

If a Mac appears later, add it as **login-only via a launchd agent**, never by taking on cgo.

Known Linux caveat to document: logind emits `Lock`/`Unlock` only when the screen locker
integrates with logind (GNOME and KDE do; a bare `i3lock`/`xss-lock` setup may not).
`SessionNew` is unconditional.

### D4 — Secrets: OS-appropriate, restricted-read storage, never in argv

| Platform | Store | Protection |
|---|---|---|
| Linux | `systemd-creds` blob + `LoadCredentialEncrypted=` in the unit | host key `/var/lib/systemd/credential.secret` is `0400 root`; plaintext lands only in `$CREDENTIALS_DIRECTORY` (tmpfs) |
| Windows | `%ProgramData%\device-activity-bot\config.json` | explicit DACL: SYSTEM + Administrators, inheritance disabled |

**Linux.** Verified on systemd 259:

```
$ sudo systemd-creds encrypt --name=bot-token plain.txt cred.enc      # 171 B
$ sudo systemd-creds decrypt --name=bot-token cred.enc -              # plaintext
$ sudo systemd-creds decrypt --name=wrong     cred.enc -
Embedded credential name 'bot-token' does not match filename 'wrong', refusing.
```

The blob is name-bound, so a ciphertext cannot be replayed under another credential name.
The ciphertext file itself needs no protection. systemd decrypts it and hands the plaintext
to the service out-of-band — it never appears in the unit, in `systemctl cat`, in `ps`, or
in the process environment.

This requires a custom unit template. `kardianos/service`'s stock systemd template emits
only `EnvironmentFile=-/etc/sysconfig/{{Name}}` (`service_systemd_linux.go:347`), so
`LoadCredentialEncrypted=` needs its `optionSystemdScript` escape hatch
(`service_systemd_linux.go:137`).

**Windows.** The ACL is the control that actually protects the token, so that is what gets
built. Set via `x/sys/windows` (`SetNamedSecurityInfo` with a hand-built DACL and
`PROTECTED_DACL_SECURITY_INFORMATION` to kill inheritance) — pure Go, no cgo.

Rejected, and why:

- **Credential Manager.** `CredWrite` with `CRED_PERSIST_LOCAL_MACHINE` is **per-account**
  — "local machine" governs persistence across logons, not visibility across accounts.
  `install` runs as an Administrator, the service as `LocalSystem`, so the service cannot
  read what the installer wrote. Bridging that needs a one-time handoff file which itself
  needs the DACL, at which point the file *is* the store.
- **DPAPI.** `CRYPTPROTECT_LOCAL_MACHINE` is decryptable by any process on the box, so it
  is no boundary against a local user; user scope has the same account gap as above.
- **gnome-keyring / Secret Service / libsecret on Linux.** Session-scoped. A root unit at
  boot has no session bus and no unlocked keyring — and frequently no keyring daemon at
  all (this dev box has none installed).

**Rule, both platforms:** secrets are passed to `install`, which persists them. They are
never service launch arguments — those leak via `systemctl cat`, `ps`, SCM config and Task
Manager.

Verify the Windows DACL on a real Windows host before tagging 2.0. `C:\ProgramData` grants
`Users` **read** by default, so an inherited-permission file there is world-readable; getting
the DACL silently wrong reproduces exactly the exposure this is meant to prevent.

### D5 — Migration accepts an existing `.env`

`install` reads `--from-env <path>` so 1.x users migrate without retyping secrets into a
shell. Interactive prompt as the alternative. Secrets never land in shell history.

### D6 — Sender authorization is an invariant

An allowlist of Telegram user IDs, checked **before** command parsing. Defaults to `CHAT_ID`:
in a private chat the chat ID is the owner's own user ID, so existing deployments need no
new configuration. A **negative** `CHAT_ID` denotes a group or channel, not a user — there
the bot refuses to start without an explicit `ALLOWED_USER_IDS`, rather than defaulting to
"every member of the group".

This closes [#56](https://github.com/dustfeather/device-activity-telegram-bot/issues/56):
1.x registered the `/halt` handler with no sender filter, so any Telegram user who found
the bot could power off the host — `/halt` with no arguments shuts down immediately. Fixed
on the Python line in `36e0883` so the `v1.0.0` tag is safe, and carried into 2.0 as a
required invariant.

`CHAT_ID` is an outbound destination. It is not, and never was, an inbound authorization.

---

## 3. Invariants the port must carry

1. `bot_token` and `chat_id` regex-validated in **both** the config loader and the HTTP
   client (SSRF defence — the token is interpolated into the API URL). Keep both in sync.
2. `DEVICENAME` regex-checked, and shutdown only when it matches the host's node name
   (command-injection / wrong-host defence).
3. Sender allowlist enforced before argument parsing (D6).
4. Secrets never in argv, never in the unit file, never in the process environment (D4).

Invariant 3 is new in 2.0. It is listed here because a faithful port reproduces a missing
check as faithfully as a present one.

---

## 4. Corrections to #34

Recorded so the issue is not re-read as authoritative on these points:

| #34 says | Correction |
|---|---|
| `kardianos/service` is "ONE library, ONE API" covering the whole service story | True for install/run/uninstall, false for session awareness. It cannot receive Windows logon/unlock — see D2. |
| Linux secrets via `EnvironmentFile=` and a custom `SystemdScript` | `EnvironmentFile` is already in the stock template, so no custom template is needed *for that*. But `systemd-creds` is the better store, and *that* does need the custom template. Net: custom template yes, for a different reason. |
| Windows secrets via "DPAPI / Credential Manager" | Both have an installer-vs-service account gap; DPAPI machine scope is no boundary at all. The ACL is the real control — see D4. |
| Ship `darwin/arm64` | Dropped from 2.0 — see D3. |
| Port the `send` one-shot notification path | No separate one-shot survives; the service emits the notification itself — see §1. |

---

## 5. Sequencing

Tag and branch first, then vertical slices — each one leaves `main` building and testable.

0. **Cut the Python line.** Tag `v1.0.0` at the Python HEAD (including `36e0883`), branch
   `maint/1.x`. Nothing Go lands before this.
1. **Skeleton.** Go module, `cmd/` layout, config loading with both regex validations and
   the allowlist, `install` / `uninstall` / `run` subcommands via `kardianos/service`.
   Service starts, sends its startup notification, exits cleanly. Python deleted from `main`
   in this slice.
2. **`/halt`.** Telegram long-poll, sender allowlist, `DEVICENAME` regex + node-name match,
   `exec.Command` shutdown per OS.
3. **Session events.** Windows `x/sys/windows/svc` + `AcceptSessionChange`; Linux logind
   D-Bus. Login/unlock notification restored — parity with 1.x reached here.
4. **Secret storage.** `systemd-creds` + custom unit template; Windows DACL'd config file.
   Verify the DACL on real Windows.
5. **Release.** Cross-compiled binaries for the three targets, `go build` / `go vet` /
   `go test` CI replacing the PyInstaller flow.
6. **Migration doc.** Uninstall the scheduled task or old systemd unit → `bot install`.

Tag `v2.0.0` after slice 5; slice 6 may follow.

---

## 6. Still open

Not blocking slice 0 or 1; resolve before the slice that needs them.

- **Telegram library** — `telego` vs `telebot` vs raw `net/http` against the Bot API.
  Outbound `sendMessage` is a plain POST either way; the question is whether inbound
  long-polling justifies a dependency. Needed for slice 2.
- **Module path and `cmd/` layout** — one binary with subcommands is settled; the package
  split is not. Needed for slice 1.
- **CI and release pipeline** — GoReleaser vs a hand-rolled build matrix; whether release
  binaries are signed. Needed for slice 5.
- **Log destination** — Windows Event Log vs stderr-to-SCM; journald vs stderr on Linux.
- **Config file format** on Windows (JSON assumed above, not decided).

---

## 7. Verification notes

Claims in this document that were checked in-session, so they can be re-checked rather than
re-argued:

- `kardianos/service` v1.3.0 accept mask and absent session support — grep of the downloaded
  module (`service_windows.go:182`; zero `WTS`/`SessionChange` hits module-wide).
- `godbus/dbus` v5.2.2 purity — sole `import "C"` is DragonflyBSD-only; `CGO_ENABLED=0`
  cross-builds succeed for linux/arm64, windows/amd64, darwin/arm64.
- `systemd-creds` encrypt/decrypt round trip and name-binding refusal, systemd 259.
- Absence of a keyring daemon on the dev box (no `gnome-keyring-daemon`, no `kwalletd`,
  no `secret-tool`) despite a live session bus.

Not verified, and flagged as such:

- The Windows DACL behaviour and `C:\ProgramData` default permissions — reasoned from
  documented semantics, no Windows host available in that session.
- Every fix in D2/D4 is an approach, not a tested recipe. None of the Go code exists yet.
