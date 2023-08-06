make

# force remove scss cache
watchmedo shell-command \
    --patterns="*.py;*.mako;*.js;*.css;*.scss" \
    --recursive \
    --command='rm -rf tags/0.00.aa/static/.sass-cache/ tags/0.00.aa/static/.webassets-cache/ ; make' \
    .
