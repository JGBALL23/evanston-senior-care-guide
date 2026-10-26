# Setting the two environment variables

Ten minutes, one browser tab and one PowerShell window.

**Never paste either value into a chat message, an email, a commit, or any
file in this folder.** They go into the Netlify dashboard and nowhere else. I
do not need to see them and I will not ask.

**Commands below use `curl.exe`, not `curl`.** On your machine `curl` is a
PowerShell alias for `Invoke-WebRequest`, which does not understand `-H` and
will throw a parameter error. The `.exe` is not a typo — it is the difference
between these working and not.

---

## Part A — Variable 1: `PLAN_VISIT_FORM_KEY`

This turns on the notification email. The key itself carries the destination
address, which is why no address of yours appears anywhere in the code.

1. Open <https://web3forms.com> in a new tab.
2. Enter the address you want notifications delivered to. Use one you check
   daily — this becomes the system's inbox.
3. They email you an access key: a long string of letters, numbers and dashes.
   **Copy it out of the email.** Do not retype it.
4. While you are on their site, open this form's settings and set **retention
   to the shortest period offered**. Their default is three years against your
   180 days.
5. Open <https://app.netlify.com>, sign in, go to project
   **evanston-senior-care-guide** → **Project configuration** →
   **Environment variables**.
6. Click **Add a variable** → **Add a single variable**.
   - Key: `PLAN_VISIT_FORM_KEY`
   - Value: paste the access key
   - Scopes: leave as all scopes
   - **Create variable**

## Part B — Variable 2: `PLAN_VISIT_EXPORT_TOKEN`

This is the password that reads records back out. You invent it; you are the
only person who ever sees it.

1. Generate one. In PowerShell, from this folder:

   ```
   node -e "console.log(require('crypto').randomBytes(24).toString('hex'))"
   ```

   You get a 48-character string.

2. **Save it in your password manager now**, before anything else. Do not
   reuse a password and do not invent one in your head — a token you can
   remember is a token someone can guess.

3. Back in Netlify: **Add a variable** → **Add a single variable**.
   - Key: `PLAN_VISIT_EXPORT_TOKEN`
   - Value: paste the generated string
   - **Create variable**

## Part C — Redeploy so the functions see them

```
npx netlify deploy --prod --dir=_dist --functions=netlify/functions --site=e25a95a5-7a87-4d1c-bae7-8c35d496dded
```

## Part D — Confirm both took, without revealing either

This reveals no secret. It tells you only whether the lock exists:

```
curl.exe -s -o NUL -w "export: %{http_code}`n" https://evanston-senior-care-guide.netlify.app/api/plan-visit-export
```

- `503` → `PLAN_VISIT_EXPORT_TOKEN` is **not** set yet
- `401` → it **is** set, and it correctly refused you because you sent no token

**`401` is the success condition.** It means the lock is real and working.

Then prove your own token opens it:

```
$t = Read-Host "paste your export token"
curl.exe -s -H "Authorization: Bearer $t" https://evanston-senior-care-guide.netlify.app/api/plan-visit-export
```

Expect `{"ok":true,"count":...}`. `Read-Host` keeps the token out of your
command history.

**The form key cannot be confirmed yet.** Checking it means submitting a real
POST, and the endpoint answers `503 collection_disabled` until collection is
switched on. That check is step 3 of the launch test below, not part of this
setup.

---

## What happens after both variables are set

Setting them does **not** turn the form on. Collection is held off by two
separate switches and neither is an environment variable:

- `const COLLECTING = false` in `app.js`
- `PLAN_VISIT_COLLECTION_ENABLED` unset in Netlify

Both stay as they are until the employer-permission question in
`LAUNCH-CHECKLIST.md` item 1 is answered. When it is, tell me and I run this,
in this order, and report the real output of every step:

1. Flip both switches, copy `staged/privacy.html` into `_dist/`, run
   `node test.js`, deploy.
2. Submit one test lead named `TEST-DELETE-ME`.
3. Confirm the server returned a `submissionId` and a `receivedAt`, and read
   the `notification` field: `sent` means the email went out, `not_configured`
   means the form key never took, `failed` means the key was rejected.
4. Retrieve the record through the authorised export and confirm the ID and
   timestamp match what the page displayed.
5. Confirm the export refuses a request carrying no token.
6. Delete the test record and every other test row until the count reads `0`.

**The form is not live until step 6 passes.** I will not describe it as live
before then, and a green `node test.js` is not that proof — it reads source
files, it does not touch the running site.

---

## If you get stuck

Tell me the HTTP status code and the `notification` value. Those two things
diagnose every failure mode this system has, and neither is a secret.
