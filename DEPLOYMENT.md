# Render and Cloudinary configuration

## 1. Create the Cloudinary account

Create a Cloudinary product environment, then open **Console → Settings → API Keys**. Copy the complete API environment variable in this format:

```text
cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

Do not commit that value to GitHub, `.env`, `render.yaml`, or screenshots. Cloudinary’s Python SDK supports this `CLOUDINARY_URL` format and the application passes uploads to Cloudinary when it is present. See the [Cloudinary Python quick start](https://cloudinary.com/documentation/python_quickstart).

## 2. Add variables in Render

In the Render Dashboard, open the `phantomvault-pro` web service, select **Environment**, choose **Add Environment Variable**, and add these values:

```text
SECRET_KEY=<long random value, or keep Render's generated value>
DATABASE_URL=<automatically supplied by the Render Postgres database>
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
APP_BASE_URL=https://<your-render-service>.onrender.com
MAX_UPLOAD_MB=12
```

`OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `AI_MODEL` are optional. The built-in evidence-first coach works without them. Save with **Save, rebuild, and deploy** so the running process receives the variables. Render documents that values are runtime strings and should be added through the Dashboard or Blueprint placeholders rather than committed in source.

The included `render.yaml` already generates `SECRET_KEY`, links `DATABASE_URL` to the Postgres service, and declares `CLOUDINARY_URL` and the optional AI key as `sync: false`. When an existing Blueprint is updated, Render does not reprompt for old `sync: false` values; add or change those secrets in the service’s Environment page.

## 3. Verify persistence

After deploy, open `/health` and confirm a JSON response with `status: ok`. Sign in, create a trade, upload a PNG or JPG screenshot, and confirm the image loads after a new deploy. The database stores the Cloudinary delivery URL, while Cloudinary stores the actual file. This avoids relying on Render’s ephemeral service filesystem.

If an upload fails, inspect Render logs for Cloudinary authentication errors. Check that the value starts with `cloudinary://`, has no quotes or trailing spaces, and uses the API key and secret from the same Cloudinary product environment.

## 4. Optional GitHub Actions deployment

The workflow in `.github/workflows/ci-cd.yml` runs tests on Python 3.11 and 3.12 for pushes and pull requests. To enable deployment after a successful push to `main`:

1. In Render, open the service’s **Settings → Deploy Hook** section and create a deploy hook.
2. In GitHub, open **Settings → Secrets and variables → Actions** and add the secret `RENDER_DEPLOY_HOOK_URL`.
3. Add the repository variable `RENDER_DEPLOY_ENABLED` with the value `true`.
4. Push to `main`. The test matrix must pass before the deploy job sends the hook request.

Keep the Render deploy hook URL secret. If you prefer Render’s native Git auto-deploy, leave `RENDER_DEPLOY_ENABLED` unset and Render will deploy from its configured repository instead.

## Official references

- [Render environment variables and secrets](https://render.com/docs/configure-environment-variables)
- [Render Blueprint environment variables](https://render.com/docs/blueprint-spec#environment-variables)
- [Cloudinary Python quick start](https://cloudinary.com/documentation/python_quickstart)
