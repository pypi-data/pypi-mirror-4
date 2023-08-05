config = string(default='')
owner  = string(default='')

[repo_ls]
show_scm    = boolean(default=False)
show_desc   = boolean(default=False)
show_access = boolean(default=False)
scm         = option(hg, git, all, default=all)
access      = option(public, private, all, default=all)

[repo_create]
private = boolean(default=True)
scm     = option(hg, git, default=hg)
clone   = boolean(default=False)
desc    = string(default='')

[repo_clone]
destdir = string(default='.')
proto   = option(http, ssh, default=http)

[repo_sync]
destdir  = string(default='.')
owner    = string(default=None)
all      = boolean(default=False)
already  = boolean(default=False)

[repo_set]
private  = boolean(default=None)
