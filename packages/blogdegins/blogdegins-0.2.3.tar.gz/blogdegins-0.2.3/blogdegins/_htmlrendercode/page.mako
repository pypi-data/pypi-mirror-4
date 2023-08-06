<%!
from ginsfsm.compat import iteritems_
%>
<!DOCTYPE html>
<!--paulirish.com/2008/conditional-stylesheets-vs-css-hacks-answer-neither/-->
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>    <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>    <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>${title}</title>

    <link rel="shortcut icon" href="favicon.ico"/>
    <link rel="apple-touch-icon" href="apple-touch-icon.png"/>

% for key, value in iteritems_(metadata):
    % if value:
    <meta name="${key}" content="${value}">
    % endif
% endfor

    <!-- Mobile viewport optimized: h5bp.com/viewport -->
    <meta name="viewport" content="width=device-width">

% for url in assets_env['css'].urls():
    <link rel="stylesheet" href="${url}">
% endfor

% for url in assets_env['top_js'].urls():
    <script src="${url}"></script>
% endfor

</head>

<body>

    <div id="global-grid-container" class="grid-container-class-100">
    ${rendered_childs}
    </div>

    <!-- JavaScript at the bottom for fast page loading -->
    % for url in assets_env['bottom_js'].urls():
    <script src="${url}"></script>
    % endfor

</body>
</html>
