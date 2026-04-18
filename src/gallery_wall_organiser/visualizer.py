import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from gallery_wall_organiser.models import Layout


def render(layout: Layout) -> Figure:
    fig, ax = plt.subplots()
    ax.set_xlim(0, layout.wall.width)
    ax.set_ylim(0, layout.wall.height)
    for p in layout.placements:
        ax.add_patch(mpatches.Rectangle((p.x, p.y), p.photo.width, p.photo.height))
    for o in layout.obstacles:
        ax.add_patch(mpatches.Rectangle((o.x, o.y), o.width, o.height))
    return fig
