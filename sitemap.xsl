<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="es-MX"><head><meta charset="utf-8"/><meta name="robots" content="noindex"/><title>Mapa del sitio · TarjetasNFC</title>
<style>body{font-family:Poppins,system-ui,sans-serif;margin:0;padding:32px 16px;color:#0b1325;background:#f5f6f8}main{max-width:1100px;margin:0 auto}
h1{font-size:1.6rem}p{color:#5b6475}table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e3e6ec;border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:10px 14px;border-bottom:1px solid #e3e6ec;font-size:.9rem}th{background:#1d5ff0;color:#fff}a{color:#1d5ff0}</style></head>
<body><main><h1>Mapa del sitio de TarjetasNFC</h1><p>Este archivo XML es para buscadores como Google y Bing.</p>
<xsl:choose>
<xsl:when test="s:sitemapindex"><table><tr><th>Sitemap</th><th>Última modificación</th></tr>
<xsl:for-each select="s:sitemapindex/s:sitemap"><tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="s:lastmod"/></td></tr></xsl:for-each></table></xsl:when>
<xsl:otherwise><table><tr><th>URL</th><th>Imágenes</th><th>Videos</th><th>Última modificación</th></tr>
<xsl:for-each select="s:urlset/s:url"><tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="count(image:image)"/></td>
<td><xsl:value-of select="count(video:video)"/></td><td><xsl:value-of select="s:lastmod"/></td></tr></xsl:for-each></table></xsl:otherwise>
</xsl:choose></main></body></html>
</xsl:template></xsl:stylesheet>
