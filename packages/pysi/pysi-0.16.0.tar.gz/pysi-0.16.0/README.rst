PySi
====

Links
-----

- repository: https://bitbucket.org/imbolc/pysi/
- russian docs: http://pysi.org/lab/pysi/

Installation
------------

::

    $ pip install pysi

Hello world
-----------

::

    import pysi
    
    @pysi.view('/')
    def home(rq):
        return 'Hello world!'
        
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        make_server('', 8000, pysi.App()).serve_forever()

Another example
---------------

::

    from pysi import cfg, view, redirect, abort
    from models import Profile
    from forms import ProfileForm

    @view('/profile/<int:id>/edit/', 'profile/edit.html')
    def edit(rq, id):
        obj = Profile.get(id)
        if not obj or obj.user != rq.user:
            abort(404)
        form = ProfileForm(rq.form)
        if rq.method == 'POST' and form.validate():
            form.populate_obj(obj)
            obj.save()
            rq.flash('Profile updated', 'success')
            return redirect('profile.edit')
        return {'form': form, 'post': post}

