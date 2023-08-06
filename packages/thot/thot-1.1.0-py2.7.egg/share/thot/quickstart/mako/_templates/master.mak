<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="${page['language']}" lang="${page['language']}">
<head>
   <meta http-equiv="content-type" content="text/html; charset=utf-8" />
   <title>${ page['title'] }</title>
   <meta name="generator" content="Thot ${ thot_version }" />
   <meta name="author" content="${ settings['author']['name'] }" />

## syntax highlighting CSS
   <link rel="stylesheet" href="/css/syntax.css" type="text/css" />

## Homepage CSS
   <link rel="stylesheet" href="/css/screen.css" type="text/css" media="screen, projection" />
</head>
<body>

<div class="site">
  <div class="title">
    <a href="/">${ settings['author']['name'] }'s Blog</a>
  </div>

  ${next.body()}

  <div class="footer">
    <div class="contact">
      <p>
        <a href="mailto:${ settings['author']['email'] }">${ settings['author']['name'] }</a>
      </p>
    </div>
    <div class="contact">
      <p>
        <a href="http://github.com/wmark/thot">powered by Thot</a>
      </p>
    </div>
    <div class="rss">
      <a href="/atom.xml"><img src="/img/rss.png" alt="Subscribe to RSS Feed" /></a>
    </div>
  </div>
</div>
</body>
</html>
