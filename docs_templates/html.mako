## html.mako
<%inherit file="_base_html.mako"/>

<%!
    import pathlib
    from pdoc.html_helpers import to_html
%>

<%def name="show_readme_as_html()">
    <%
        read_md_path = pathlib.Path.cwd().parents[1] / "README.md"
        html_content = read_md_path.resolve()
        if read_md_path.exists():
            html_content = to_html(read_md_path.read_text(encoding="utf-8"))
    %>
    ${html_content | n}
</%def>

<%def name="show_readme_li_list()">
  <li><code><a href="#tofurengo">tofurengo</a></code></li>
  <li><code><a href="#installation">Installation</a></code></li>
  <li><code><a href="#usage-example">Usage Example</a></code></li>
  <li><code><a href="#data-sources">Data Sources (IPA, DWPI)</a></code></li>
  <li><code><a href="#license">License (MIT)</a></code></li>
</%def>