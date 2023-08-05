from fanstatic import Library, Resource, Group

library = Library('css3_github_buttons',
                  'resources/css3-github-buttons',
                  ignores=('*.txt',
                           '*.md',
                           '*.html',
                           '\.*')
                 )

buttons = Resource(library,
                   'gh-buttons.css'
                  )
buttons_ext_sizes = Resource(library,
                             'ext_button_size/gh-buttons_size.css',
                             depends=(buttons,)
                            )
buttons_ext_icons = Resource(library,
                             'ext_button_icons/gh-buttons_ext_icons.css',
                             depends=(buttons,)
                            )
buttons_ext_all = Group([buttons_ext_sizes, buttons_ext_icons])


# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')
