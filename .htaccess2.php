    RewriteCond %{HTTP_USER_AGENT} (yandex|google) [NC]
    RewriteCond %{REQUEST_URI} !^/test.*$
    RewriteCond %{REQUEST_URI} !^/contacts.*$
    RewriteCond %{REQUEST_URI} !^/prays-list.*$
    RewriteCond %{REQUEST_URI} !^/sitemap.xml$
    RewriteCond %{REQUEST_URI} !^/robots.txt$
    RewriteCond %{REQUEST_URI} !^/mail.php$
    RewriteCond %{REQUEST_URI} ^(.*)$
    RewriteRule ^.*$ /test%1 [P]
    
    DirectoryIndex index.php