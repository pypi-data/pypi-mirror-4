function xhostplus_social_inject_js(url, content) {
    var script = document.createElement('SCRIPT')
    var head = document.getElementsByTagName('HEAD')[0];

    script.type = 'text/javascript';
    script.async = true;
    script.src = url;

    if(content) {
        content = document.createTextNode(content);
        script.appendChild(content);
    }

    head.appendChild(script);
}
