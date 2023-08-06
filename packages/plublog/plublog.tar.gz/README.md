##What is plublog?

Plublog is a static blog generator. It lets you can extend your blog by plugins and theme.

##Can I use plublog?

You just need that you can type command in Linux. However, if you know some things about Python, it will be more better :)

##How to use it?

###To use plublog, you must download the plublog first:
```bash
git clone git://github.com/rephaslife/plublog.git
```

###Install plublog:
```bash
cd plublog
python setup.py install
```

###Then, inital the plublog where you want to place you blog:
```bash
cd place-of-your-blog
plublog init
```

###Choose your theme and place into the folder "theme":
```bash
cd theme
#download your theme. like: git clone git://github.com/rephaslife/greenray.git
```

###Create your first article.
```bash
cd abspath-os-place-of-your-blog
cd posts
touch your-article.html
vim your-article.html
```
> NOTE: Name of the article **MUST** end with *.html* !

###Now, build your blog!
```bash
cd abspath-os-place-of-your-blog
plublog build
```

-----

After run `plublog build`, you can see your site's static file in folder "site".

-----

Enjoy plublog!

