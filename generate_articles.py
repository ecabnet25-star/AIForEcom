from pathlib import Path
import re

repo = Path(__file__).resolve().parent
md_path = Path(r'C:\Users\Ethan\Downloads\AIForEcom-Articles.md')
text = md_path.read_text(encoding='utf-8')
entries = re.split(r'^# Article \d+: ', text, flags=re.MULTILINE)[1:]
if len(entries) != 10:
    raise SystemExit(f'Expected 10 articles, found {len(entries)}')

mapping = {
    'best-ai-tools-shopify.html': ('Hub guide','Best AI Tools for Shopify Stores (2026)'),
    'ai-product-description-generators.html': ('Comparison','AI Product Description Generators: Honest Review (2026)'),
    'ai-amazon-listing-optimisation.html': ('Tutorial','How to Use AI to Write Amazon Listing Titles and Bullet Points'),
    'tidio-vs-gorgias.html': ('Comparison','Tidio vs Gorgias — Which AI Customer Support Tool Is Right for Your Store?'),
    'jasper-ai-review-ecommerce.html': ('In-depth review','Jasper AI Review for E-Commerce — Is It Worth It for Shopify Sellers?'),
    'jasper-vs-copyai-ecommerce.html': ('Comparison','Jasper vs Copy.ai for E-Commerce — Which Is Better in 2026?'),
    'best-ai-tools-etsy-sellers.html': ('Platform guide','Best AI Tools for Etsy Sellers (2026)'),
    'ai-ecommerce-email-marketing.html': ('Tutorial','How to Use AI for E-Commerce Email Marketing (Omnisend vs Klaviyo)'),
    'ai-product-photo-tools.html': ('Listicle','AI Product Photo Tools for Shopify'),
    'shopify-ai-tool-stack.html': ('Stack guide','The AI Tool Stack Every Shopify Store Should Have in 2026 (Under $100/Month)'),
}
filenames = list(mapping.keys())

# helper functions

def sentence_summary(paragraph):
    paragraph = paragraph.strip()
    if not paragraph:
        return ''
    m = re.search(r'([^.?!]*[.?!])', paragraph)
    if m:
        return m.group(1).strip()
    return paragraph


def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def inline_format(text):
    text = escape_html(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def render_table(lines):
    rows = [[cell.strip() for cell in l.strip().strip('|').split('|')] for l in lines]
    html = ['<div class="table-wrapper">', '<table>']
    if len(rows) >= 2 and re.match(r'^\s*[-:]+', rows[1][0]):
        header = rows[0]
        html.append('<thead><tr>' + ''.join(f'<th>{inline_format(cell)}</th>' for cell in header) + '</tr></thead>')
        body = rows[2:]
    elif len(rows) >= 2 and all(re.match(r'^[-:]+$', cell) for cell in rows[1]):
        header = rows[0]
        html.append('<thead><tr>' + ''.join(f'<th>{inline_format(cell)}</th>' for cell in header) + '</tr></thead>')
        body = rows[2:]
    else:
        body = rows
    if body:
        html.append('<tbody>')
        for row in body:
            html.append('<tr>' + ''.join(f'<td>{inline_format(cell)}</td>' for cell in row) + '</tr>')
        html.append('</tbody>')
    html.append('</table></div>')
    return html


def convert_markdown_to_html(md):
    lines = md.splitlines()
    html_lines = []
    in_ul = in_ol = in_code = False
    code_tag = False
    table_lines = []
    for line in lines:
        if line.startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                html_lines.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            html_lines.append(escape_html(line))
            continue
        if line.strip() == '' or line.strip() == '---':
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            if table_lines:
                html_lines.extend(render_table(table_lines))
                table_lines = []
            continue
        if line.startswith('### '):
            if in_ul:
                html_lines.append('</ul>'); in_ul=False
            if in_ol:
                html_lines.append('</ol>'); in_ol=False
            if table_lines:
                html_lines.extend(render_table(table_lines)); table_lines=[]
            html_lines.append(f'<h3>{inline_format(line[4:])}</h3>')
            continue
        if line.startswith('## '):
            if in_ul:
                html_lines.append('</ul>'); in_ul=False
            if in_ol:
                html_lines.append('</ol>'); in_ol=False
            if table_lines:
                html_lines.extend(render_table(table_lines)); table_lines=[]
            html_lines.append(f'<h2>{inline_format(line[3:])}</h2>')
            continue
        if re.match(r'^\|', line):
            table_lines.append(line)
            continue
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            if in_ul:
                html_lines.append('</ul>'); in_ul=False
            if not in_ol:
                html_lines.append('<ol>'); in_ol=True
            html_lines.append(f'<li>{inline_format(m.group(2))}</li>')
            continue
        if line.startswith('- ') or line.startswith('* '):
            if in_ol:
                html_lines.append('</ol>'); in_ol=False
            if not in_ul:
                html_lines.append('<ul>'); in_ul=True
            html_lines.append(f'<li>{inline_format(line[2:])}</li>')
            continue
        if table_lines:
            html_lines.extend(render_table(table_lines))
            table_lines = []
        if in_ul:
            html_lines.append('</ul>'); in_ul=False
        if in_ol:
            html_lines.append('</ol>'); in_ol=False
        html_lines.append(f'<p>{inline_format(line)}</p>')
    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')
    if in_code:
        html_lines.append('</code></pre>')
    if table_lines:
        html_lines.extend(render_table(table_lines))
    return '\n'.join(html_lines)


def apply_intro(html):
    lines = html.split('\n')
    for idx, line in enumerate(lines):
        if line.startswith('<p>'):
            lines[idx] = line.replace('<p>', '<p class="article-intro">', 1)
            break
    return '\n'.join(lines)

base_template = '''<!DOCTYPE HTML>
<html>
  <head>
    <title>{title} — AIForEcom</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <meta name="description" content="{description}" />
    <link rel="stylesheet" href="assets/css/main.css" />
    <noscript><link rel="stylesheet" href="assets/css/noscript.css" /></noscript>
    <style>
      /* Nav */
      #site-nav {{
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        background: rgba(36,41,67,0.97); display: flex;
        align-items: center; justify-content: space-between;
        padding: 0 2em; height: 54px;
      }}
      #site-nav .nav-logo {{
        font-size: 1.1em; font-weight: 600; color: #fff;
        text-decoration: none; letter-spacing: 0.03em;
      }}
      #site-nav ul {{ list-style: none; display: flex; gap: 0.2em; margin: 0; padding: 0; }}
      #site-nav ul li a {{
        color: rgba(255,255,255,0.75); text-decoration: none;
        font-size: 0.82em; letter-spacing: 0.08em; text-transform: uppercase;
        padding: 0.5em 0.9em; border-radius: 4px;
        transition: color 0.2s, background 0.2s;
      }}
      #site-nav ul li a:hover {{ color: #fff; background: rgba(255,255,255,0.1); }}
      #site-nav ul li a.nav-highlight {{
        color: #fff; background: rgba(99,179,237,0.25);
        border: 1px solid rgba(99,179,237,0.5);
      }}
      body {{ padding-top: 54px; }}

      /* Article layout */
      .article-wrap {{
        max-width: 740px;
        margin: 0 auto;
        padding: 4em 2em 5em;
      }}
      .article-wrap .article-meta {{
        font-size: 0.78em;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6366f1;
        font-weight: 700;
        margin-bottom: 0.8em;
      }}
      .article-wrap h1 {{
        font-size: 2em;
        line-height: 1.25;
        color: #1a1a2e;
        margin-bottom: 0.6em;
      }}
      .article-wrap .article-intro {{
        font-size: 1.08em;
        color: #444;
        line-height: 1.7;
        border-left: 3px solid #6366f1;
        padding-left: 1em;
        margin-bottom: 2em;
      }}
      .article-wrap h2 {{
        font-size: 1.3em;
        color: #1a1a2e;
        margin: 2em 0 0.5em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid #e8eaf0;
      }}
      .article-wrap h3 {{
        font-size: 1.05em;
        color: #1a1a2e;
        margin: 1.5em 0 0.4em;
        font-weight: 700;
      }}
      .article-wrap p {{
        font-size: 0.95em;
        line-height: 1.8;
        color: #333;
        margin-bottom: 1.2em;
      }}
      .article-wrap ul, .article-wrap ol {{
        margin: 0 0 1.2em 1.5em;
        font-size: 0.95em;
        line-height: 1.8;
        color: #333;
      }}
      .article-wrap ul li {{ list-style: disc; }}
      .article-wrap ol li {{ list-style: decimal; }}
      .article-wrap table {{
        width: 100%; border-collapse: collapse;
        font-size: 0.88em; margin: 1.5em 0;
      }}
      .article-wrap table th {{
        background: #f3f4f6; text-align: left;
        padding: 0.6em 0.8em; font-weight: 700;
        border: 1px solid #e2e4e9; color: #1a1a2e;
      }}
      .article-wrap table td {{
        padding: 0.55em 0.8em;
        border: 1px solid #e2e4e9;
        color: #333;
      }}
      .article-wrap table tr:nth-child(even) td {{ background: #f9fafb; }}
      .article-wrap code {{
        background: #f3f4f6; border-radius: 4px;
        padding: 0.15em 0.4em; font-size: 0.88em;
        font-family: 'Courier New', monospace; color: #4f46e5;
      }}
      .article-wrap pre {{
        background: #1e1e2e; border-radius: 6px;
        padding: 1.2em 1.4em; margin: 1.4em 0;
        overflow-x: auto;
      }}
      .article-wrap pre code {{
        background: none; color: #cdd6f4;
        font-size: 0.85em; padding: 0;
      }}
      .article-wrap blockquote {{
        border-left: 3px solid #6366f1;
        margin: 1.5em 0; padding: 0.8em 1.2em;
        background: #f5f5ff; border-radius: 0 6px 6px 0;
        color: #444; font-style: italic;
      }}
      .affiliate-note {{
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 6px; padding: 1em 1.2em;
        font-size: 0.82em; color: #166534;
        margin: 2.5em 0 1em;
      }}
      .back-link {{
        display: inline-block;
        font-size: 0.82em; font-weight: 700;
        letter-spacing: 0.06em; text-transform: uppercase;
        color: #6366f1; text-decoration: none;
        margin-bottom: 2em;
      }}
      .back-link::before {{ content: "← "; }}
      .back-link:hover {{ color: #4f46e5; }}

      @media screen and (max-width: 640px) {{
        #site-nav ul {{ display: none; }}
        .article-wrap {{ padding: 2.5em 1.2em 4em; }}
        .article-wrap h1 {{ font-size: 1.5em; }}
      }}
    </style>
  </head>
  <body class="is-preload">

    <nav id="site-nav">
      <a href="index.html" class="nav-logo">AIForEcom</a>
      <ul>
        <li><a href="index.html#articles">Reviews</a></li>
        <li><a href="index.html#articles">Comparisons</a></li>
        <li><a href="index.html#articles">Tutorials</a></li>
        <li><a href="index.html#tools">Top Tools</a></li>
        <li><a href="stack-finder.html" class="nav-highlight">AI Stack Finder</a></li>
      </ul>
    </nav>

    <section class="main style1">
      <div class="article-wrap">

        <a href="index.html" class="back-link">Back to all articles</a>

        <p class="article-meta">{meta}</p>
        <h1>{title}</h1>
        <p class="article-intro">{intro}</p>

        {body}

        {cta}
        <div class="affiliate-note">
          Some links in this article are affiliate links. If you sign up for a tool through a link on this page, we may earn a small commission at no extra cost to you. We only recommend tools we've actually tested.
        </div>

      </div>
    </section>

    <section id="footer">
      <ul class="copyright">
        <li>&copy; 2026 AIForEcom</li>
        <li><a href="affiliate-disclosure.html">Affiliate disclosure</a></li>
        <li>Design: <a href="http://html5up.net">HTML5 UP</a></li>
      </ul>
    </section>

    <script src="assets/js/jquery.min.js"></script>
    <script src="assets/js/jquery.scrolly.min.js"></script>
    <script src="assets/js/browser.min.js"></script>
    <script src="assets/js/breakpoints.min.js"></script>
    <script src="assets/js/util.js"></script>
    <script src="assets/js/main.js"></script>

  </body>
</html>
'''

cta_map = {
    'tidio-vs-gorgias.html': '<ul class="actions" style="margin-top:2em">\n  <li><a href="https://www.tidio.com/?ref=aiforecom" class="button primary" target="_blank" rel="noopener">Try Tidio free</a></li>\n</ul>',
    'ai-ecommerce-email-marketing.html': '<ul class="actions" style="margin-top:2em">\n  <li><a href="https://www.omnisend.com/?ref=aiforecom" class="button primary" target="_blank" rel="noopener">Try Omnisend free</a></li>\n</ul>',
    'shopify-ai-tool-stack.html': '<div style="background:#f5f5ff;border:1px solid #c7d2fe;border-radius:6px;padding:1.4em 1.6em;margin:2em 0;">\n  <strong>Not sure which stack suits your store?</strong>\n  <p style="margin:0.5em 0 1em">Take our free AI Stack Finder quiz — five questions, personalised recommendation, no email required.</p>\n  <ul class="actions">\n    <li><a href="stack-finder.html" class="button primary">Take the AI Stack Finder</a></li>\n  </ul>\n</div>'
}

for idx, filename in enumerate(filenames):
    meta, title = mapping[filename]
    art_title, raw_body = entries[idx].split('\n',1)
    lines = raw_body.splitlines()
    content_start = 0
    for i,line in enumerate(lines):
        if line.strip() == '---':
            content_start = i+1
            break
    while content_start < len(lines) and lines[content_start].strip() == '':
        content_start += 1
    body_text = '\n'.join(lines[content_start:]).strip()
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', body_text) if p.strip()]
    desc = sentence_summary(paragraphs[0]) if paragraphs else title
    body_html = convert_markdown_to_html(body_text)
    body_html = apply_intro(body_html)
    cta = cta_map.get(filename, '')
    content = base_template.format(title=title, description=desc.replace('"','&quot;'), meta=meta, intro=paragraphs[0].replace('"','&quot;'), body=body_html, cta=cta)
    out_path = repo / filename
    out_path.write_text(content, encoding='utf-8')
    print(f'Wrote {filename}')
