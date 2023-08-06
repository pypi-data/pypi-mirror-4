import fanstatic
import js.raphael


library = fanstatic.Library('graphael', 'resources')


g_raphael = fanstatic.Resource(
    library,
    'g.raphael.js',
    minified='g.raphael-min.js',
    depends=[js.raphael.raphael])


bar = fanstatic.Resource(
    library,
    'g.bar.js',
    minified='g.bar-min.js',
    depends=[g_raphael])


dot = fanstatic.Resource(
    library,
    'g.dot.js',
    minified='g.dot-min.js',
    depends=[g_raphael])


line = fanstatic.Resource(
    library,
    'g.line.js',
    minified='g.line-min.js',
    depends=[g_raphael])


pie = fanstatic.Resource(
    library,
    'g.pie.js',
    minified='g.pie-min.js',
    depends=[g_raphael])


graphael = fanstatic.Group([
    g_raphael,
    bar,
    dot,
    line,
    pie,
    ])
