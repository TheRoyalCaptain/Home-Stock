# Home Stock

Home Stock is a self-hosted household inventory and expiry tracker for umbrelOS. It combines the simple fridge overview of Fridge Assistant with practical Grocy-style stock features and printable DYMO labels.

## Login and users (v0.2.2)

Every inventory page and API endpoint requires login. First login: username
`admin`, password `admin`. You must replace this password before accessing data.
New passwords must contain 12–256 characters. Change the default immediately
on your trusted local network before exposing the application elsewhere.

Administrators can create accounts under **Gebruikers beheren**, assigning a
user or administrator role. Every new account must replace its temporary password.
Both roles share the household inventory. Profiles used for activity records
are linked to login accounts and cannot be impersonated through API parameters.
Only administrators can create users and change system settings.

Passwords use salted scrypt hashes. Opaque server-side sessions expire after
12 hours and are revoked on logout or password changes. Write requests require
CSRF tokens. Five login attempts per 15 minutes are allowed per username and
source address. Behind Umbrel's proxy the address limit may be shared.
Application exports exclude authentication tables and session secrets.

Use HTTPS for encrypted access, especially outside your local network.
For TLS terminated at a reverse proxy, set `HOME_STOCK_SECURE_COOKIE=1` on the
web container. Plain HTTP remains supported for local Umbrel installations,
but cannot protect passwords or session cookies against network interception.
The application does not configure TLS or certificates on your server.

Run authentication regression checks with `python -m unittest discover -s tests`.

## Features in v0.2.0

- Normalized SQLite database with automatic v0.1 migration
- Separate stock lots with FIFO ordering, prices, stores and expiry dates
- Fixed Koelkast, Vriezer and Voorraadkast locations plus custom locations
- Retail barcode lookup through Open Food Facts and local HS lot barcodes
- Automatic editable shelf-life estimates from local rules and optional Gemini Free Tier
- Consumption, waste, spending and store statistics
- Household profiles and complete activity history
- Low-stock and expiration notification center
- Automatic and manual shopping lists
- Recipes, ingredient stock matching and meal planning
- DYMO label confirmation, queue and browser printing (57 × 32 or 101 × 54 mm)
- CSV export, full JSON backup and responsive Dutch interface

## Install on Umbrel

1. In the Umbrel App Store, open the menu for Community App Stores.
2. Add `https://github.com/TheRoyalCaptain/Home-Stock`.
3. Open **Home Stock** in the new **Home Stock App Store** section and install it.

The Docker image is built automatically by GitHub Actions for AMD64 and ARM64. After the first push, wait for the `Build container image` workflow to finish before installing.

## Local development

```bash
docker build -t home-stock .
docker run --rm -p 8080:8080 -v home-stock-data:/data home-stock
```

Then open <http://localhost:8080>.

## Printer note

The first release prints through the browser's print dialog. Select the DYMO LabelWriter and set paper size to 57 × 32 mm with margins disabled. Direct USB printing from the Umbrel server is planned as an optional print service.

## License

MIT
