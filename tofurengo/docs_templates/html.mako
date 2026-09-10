## html.mako
## https://docs.makotemplates.org/en/latest/inheritance.html#nesting-blocks
<%inherit file="_base_html.mako"/>

<%!
    import pathlib
    # pdoc3の内部ヘルパーをインポート
    from pdoc.html_helpers import to_html
%>

<%def name="title()">
  オーバーライドタイトル:${pathlib.Path.cwd().parents[1]}
</%def>

<%def name="get_readme_md()">
    <%
        md_path = pathlib.Path.cwd().parents[1] / "README.md"
        md_content = md_path.resolve()
        if md_path.exists():
            md_content = md_path.read_text(encoding="utf-8")
    %>
    ## エスケープを防ぐために「| n」を付与
    ${md_content | n}
</%def>

<%def name="show_readme_as_html()">
    <%
        read_md_path = pathlib.Path.cwd().parents[1] / "README.md"
        html_content = read_md_path.resolve()
        if read_md_path.exists():
            html_content = to_html(read_md_path.read_text(encoding="utf-8"))
    %>
    ## エスケープを防ぐために「| n」を付与
    ${html_content | n}
</%def>