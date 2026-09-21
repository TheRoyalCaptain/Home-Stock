# Home Stock

Home Stock is a self-hosted household inventory and expiry tracker for umbrelOS. It combines the simple fridge overview of Fridge Assistant with practical Grocy-style stock features and printable DYMO labels.

## Features in v0.1.0

- Dashboard with total stock, low-stock and expiring-soon counters
- Products with quantity, minimum stock, location, category, barcode and expiry date
- Quick stock adjustments
- Automatic shopping list based on minimum stock, plus manual items
- Expiry overview
- DYMO-friendly label preview and browser printing (57 × 32 mm default)
- SQLite persistence, CSV export and JSON backup
- Responsive Dutch web interface

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
