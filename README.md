# Home Stock

Home Stock is a self-hosted household inventory and expiry tracker for umbrelOS. It combines the simple fridge overview of Fridge Assistant with practical Grocy-style stock features and printable DYMO labels.

## Vertical food labels (v0.4.0)

DYMO 99014 labels now print in portrait at 54 × 101 mm. The food-storage layout
shows the storage location, homemade/store type, product name, permanent
five-character article code, scannable lot barcode, contents or ingredients,
production/preparation date, expiry date, quantity, the person who stored it,
brand/category and lot number.

Every product receives a permanent code made from two letters and three digits,
such as `VP001` for Vegetarische pasta. Products sharing the same initials are
numbered consecutively. Existing products receive codes automatically during the
database migration. The short code identifies the product; the barcode and lot
number continue to identify the individual container or batch.

The product form distinguishes **Zelfgemaakt / bak eten** from **Winkelproduct**.
It includes contents/ingredients and a production or preparation date. Store
products can leave that date empty; the label then shows the date on which the
item was stored. The existing retail barcode and brand fields remain available.

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

## Direct USB printing (v0.3.0)

The Umbrel app includes an internal CUPS service for a USB-connected DYMO
LabelWriter 400 or 450. It discovers the printer automatically, installs the
matching open-source DYMO CUPS queue, and prints the PDF label directly from the
server. The printer service is reachable only by the Home Stock web container;
it does not expose a CUPS port on the host or local network. Only the printer
sidecar receives access to `/dev/bus/usb`, using the USB character-device cgroup
rule instead of privileged container mode.

After updating, keep the printer connected and powered on. Open **Instellingen →
Labels en meldingen**, select **Direct via USB-printer op de server**, choose the
detected printer (or automatic selection), save, and use **Testlabel direct
printen**. Label confirmation then uses direct server printing by default.
Browser printing remains available from the label preview.

Supported here: the DYMO LabelWriter 400 and 450 families using CUPS' DYMO
driver. The newer 5-series protocol is not part of this integration.

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
- DYMO label confirmation, queue, direct USB printing and browser printing
  (57 × 32 or 101 × 54 mm)
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

When using browser printing, select the DYMO LabelWriter and set paper size to
57 × 32 mm with margins disabled. Direct USB printing is the default in the
Umbrel app and requires no separate CUPS configuration.

## License

MIT
