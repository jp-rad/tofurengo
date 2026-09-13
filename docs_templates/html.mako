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

<%def name="show_links_index()">
  <li><h3>Links</h3>
    <ul>
      <li><code><a href="https://jp-rad.github.io/tofurengo/specification.ja.html" target="_blank">Specification (Japanese)</a></code></li>
      <li><code><a href="https://www.digital.go.jp/policies/local_governments/character-specification" target="_blank">Japan Std Admin Kanji</a></code></li>
      <li><code><a href="https://github.com/jp-rad/tofurengo" target="_blank">GitHub Repository</a></code></li>
      <li><code><a href="https://jp-rad.github.io/tofurengo/">This GitHub Page</a></code></li>
    </ul>
  </li>
</%def>
