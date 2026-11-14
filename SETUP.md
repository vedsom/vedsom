# Setup (about 10 minutes)

1. **Repo**: use (or create) a public repo named exactly `vedsom/vedsom`. Copy everything in this folder into it
   (including the hidden `.github/` folder), replacing the old README.md.
2. **Your portrait**: `pip install -r requirements.txt`, then
   `python scripts/ascii_svg.py photo.jpg --out assets/terminal-ascii.svg`
   Preview first with `--static`. Tweak with `--cols 90`, `--contrast 1.6`, `--invert yes|no`.
3. **Stats**: push to GitHub, open the repo's Actions tab, run "Update profile stats" once via "Run workflow".
   It then refreshes daily. For private contributions, add a `PROFILE_TOKEN` secret (a PAT with `read:user`).
4. **Snake (optional)**: run "Generate contribution snake" once from the Actions tab. Delete that README section if you skip it.
5. **README**: replace the `#` project links, add GIFs to `assets/`, and uncomment the `<img>` lines.
6. Pin your best repos on your profile page.

## Portrait already generated
`assets/terminal-ascii.svg` was built from `source/portrait_cutout.png` (head-and-shoulders crop, background removed).
To redo it: `python scripts/ascii_svg.py source/portrait_cutout.png --out assets/terminal-ascii.svg --cols 84 --contrast 1.35 --gamma 0.6`
(`--gamma` lower = fuller face, higher = more contrast; `--cols` = detail.) Delete the `source/` folder before pushing if you don't want the cutout public.
