<%namespace name="logo" file="templates/logo.mako"/>

<div id="main-content" class="grid-content-class">
    <header>
    ${logo.logo()}
    </header>

    <div class="grid-container-class-100">
    ${rendered_childs}
    </div>

    <footer>
        <span style="unicode-bidi:bidi-override; direction: rtl;">
        <%
            revchars = list('ginsmar@artgins.com') # string -> list of chars
            revchars.reverse()              # inplace reverse the list
            revchars = ''.join(revchars)    # list of strings -> string
        %>
        ${revchars}
        </span>
    </footer>

</div>
