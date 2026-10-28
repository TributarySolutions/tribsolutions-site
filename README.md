# Tributary Solutions

Static website for Tributary Solutions, LLC — water resources consulting.

## Live site

[www.tribsolutions.com](https://www.tribsolutions.com)

Hosted on GitHub Pages. The `main` branch deploys automatically.

## Files

```
index.html          Homepage
contact.html        Contact page
assets/
  styles.css        All site CSS
  logo.png          Tributary Solutions logo
  favicon.png       Browser tab icon
  jordan.jpg        Jordan Lanini portrait
  marlena.jpg       Marlena Lanini portrait
  hank.jpg          Hank (Office Dog) photo
CNAME               Custom domain configuration for GitHub Pages
```

## Making changes

Edit HTML or CSS directly, then commit and push to `main`. GitHub Pages
redeploys automatically — usually live within 60 seconds.

## Google Form link

The contact buttons link to a Google Form. To update the URL, search for
`forms.gle` in `index.html` and `contact.html`. Each occurrence has a
comment marking it:

```
<!-- Google Form contact link — replace this URL if the form address changes -->
```

## Photo crop / face centering

Face position in profile photos is controlled by `object-position` in
`assets/styles.css`. Look for `.photo-jordan`, `.photo-marlena`, and
`.photo-hank` and adjust the percentage values (higher Y% moves the crop
window down).


## Contact button

The homepage button links to `contact.html`. The contact page includes a placeholder button. Replace `href="#"` in `contact.html` with a Google Form link if you want a no-email contact workflow.

## Colors

The exact Google Sites theme variables are not exposed cleanly in the public text view. The main theme colors are defined at the top of `assets/styles.css` so they can be changed quickly:

```css
--accent: #2f6652;
--accent-dark: #21493a;
--accent-soft: #edf4f0;
```
