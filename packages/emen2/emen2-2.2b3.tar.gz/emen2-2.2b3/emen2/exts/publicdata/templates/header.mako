<%namespace name="buttons" file="/buttons"  />

<div id="nav" role="nav">
    <ul class="e2l-menu e2l-cf">

        <li>
            <a style="padding:0px;padding-left:8px;" href="${EMEN2WEBROOT}/"><img id="logo" src="${EMEN2WEBROOT}/static/images/${EMEN2LOGO}" alt="${EMEN2DBNAME}" /></a>
        </li>
    
        <li><a href="${EMEN2WEBROOT}/">Home ${buttons.caret()}</a>
            <ul>
                <li><a href="${EMEN2WEBROOT}/records/">Sitemap</a></li>
                <li class="e2l-menu-divider"><a href="${EMEN2WEBROOT}/paramdefs/">Params</a></li>
                <li><a href="${EMEN2WEBROOT}/recorddefs/">Protocols</a></li>
                <li class="e2l-menu-divider"><a href="${EMEN2WEBROOT}/users/">Users</a></li>
                <li><a href="${EMEN2WEBROOT}/groups/">User groups</a></li>
                <li class="e2l-menu-divider"><a href="${EMEN2WEBROOT}/help/">Help</a></li>                
            </ul>
        </li>

        <li>
            <a href="${EMEN2WEBROOT}/query/">Query ${buttons.caret()}</a>
            <ul>
                <li><a href="${EMEN2WEBROOT}/query">All records</a></li>
                <li><a href="${EMEN2WEBROOT}/query/rectype.is.grid_imaging/">Imaging sessions</a></li>
                <li><a href="${EMEN2WEBROOT}/query/rectype.is.image_capture*/">Images</a></li>
                <li><a href="${EMEN2WEBROOT}/query/rectype.is.labnotebook/">Lab notebooks</a></li>
                <li><a href="${EMEN2WEBROOT}/query/rectype.is.publication*/">Publications</a></li>
            </ul>
        </li>
            
    </ul>
</div>