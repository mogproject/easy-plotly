from collections import defaultdict
import yaml
import networkx as nx
import plotly.graph_objects as go
from typing import Any, List, Mapping, Tuple, Union, Callable
from IPython.display import display, Image, SVG
import math

# custom types
Vertex = Any
Edge = Tuple[Vertex, Vertex]
Num = Union[int, float]
Coord2D = Union[Num, Num]
Coord3D = Union[Num, Num, Num]
Coord = Union[Coord2D, Coord3D]


class PlotlyGraph:
    """
    (1) PlotGraph constructor parameter
    (2) NetworkX Graph attributes
    (3) Config YAML
    (4) Default
    x: configurable (dict-like, function-like, or a constant value)

                            ---> fallback
                          (1)   (2)                (3)                      (4)
    node_text              x    ---                ---                       x
    node_text_position     x   `text_position`    `node.textposition`       ---
    node_text_font_color   x   `text_font_color`  `node.textfont.color`     ---
    node_text_font_family  x   `text_font_family` `node.textfont.family`    ---
    node_text_font_size    x   `text_font_size`   `node.textfont.size`      ---
    node_size              x   `size`             `node.marker.size`        ---
    node_color             x   `color`            `node.marker.color`       ---
    node_border_width      x   `line_width`       `node.marker.line.width`  ---
    node_border_color      x   `line_color`       `node.marker.line.color`  ---
    node_opacity           x    ---               `node.marker.opacity`     ---
    edge_text              x   `text`             `edge.text`               ---
    edge_text_font_color   x   `text_font_color`  `edge.textfont.color`     ---
    edge_text_font_family  x   `text_font_family` `edge.textfont.family`    ---
    edge_text_font_size    x   `text_font_size`   `edge.textfont.size`      ---
    edge_text_offset       x   `text_offset`      `edge.textoffset`         ---
    edge_width             x   `width`            `edge.width`              ---
    edge_color             x   `color`            `edge.color`              ---
    edge_opacity           x    ---               `edge.opacity`            ---
    edge_arrow_show        x   `arrow_show`       `edge.arrow.show`         ---
    """

    def __init__(
        self, G: nx.Graph,
        config_path: str = None,
        node_text: Union[Mapping[Vertex, str], Callable] = None,
        node_text_position: Union[Mapping[Vertex, str], Callable, str] = None,
        node_text_font_color: Union[Mapping[Vertex, str], Callable, str] = None,
        node_text_font_family: Union[Mapping[Vertex, str], Callable, str] = None,
        node_text_font_size: Union[Mapping[Vertex, Num], Callable, str] = None,
        node_size: Union[Mapping[Vertex, Num], Callable, Num] = None,
        node_color: Union[Mapping[Vertex, Union[str, Num]], Callable, Union[str, Num]] = None,
        node_border_width: Union[Mapping[Vertex, Num], Callable, Num] = None,
        node_border_color: Union[Mapping[Vertex, str], Callable, str] = None,
        node_opacity: Num = None,
        edge_width: Union[Mapping[Edge, Num], Callable, Num] = None,
        edge_color: Union[Mapping[Edge, str], Callable, str] = None,
        edge_opacity: Num = None,
        edge_text: Union[Mapping[Edge, str], Callable, str] = None,
        edge_text_font_color: Union[Mapping[Edge, str], Callable, str] = None,
        edge_text_font_family: Union[Mapping[Edge, str], Callable, str] = None,
        edge_text_font_size: Union[Mapping[Edge, Num], Callable, Num] = None,
        edge_text_offset: Union[Mapping[Edge, str], Callable, str] = None,
        edge_arrow_show: Union[Mapping[Edge, bool], Callable, bool] = None,
        title: str = None,
    ) -> None:
        if config_path is None:
            self.conf = {}
        else:
            with open(config_path, 'r') as f:
                self.conf = yaml.safe_load(f)

        self.G = G

        self.nodes = G.nodes()
        self.edges = G.edges()

        self.conf['layout']['title']['text'] = title

        # configure node text
        if callable(node_text):
            self.conf['node']['text'] = [node_text(v) for v in self.nodes]
        elif isinstance(node_text, dict):
            self.conf['node']['text'] = [node_text.get(v, str(v)) for v in self.nodes]
        else:
            self.conf['node']['text'] = [str(v) for v in self.nodes]

        # configure edge text
        if callable(edge_text):
            self.conf['edge']['text'] = {e: edge_text(e) for e in self.edges}
        elif isinstance(edge_text, dict):
            self.conf['edge']['text'] = {e: edge_text.get(e, '') for e in self.edges}
        else:
            self.conf['edge']['text'] = ''

        # configure other settings
        self.conf['node']['textposition'] = self._configure_node_setting(node_text_position, 'text_position', self.conf['node']['textposition'])
        self.conf['node']['textfont']['color'] = self._configure_node_setting(node_text_font_color, 'text_font_color', self.conf['node']['textfont']['color'])
        self.conf['node']['textfont']['family'] = self._configure_node_setting(node_text_font_family, 'text_font_family', self.conf['node']['textfont']['family'])
        self.conf['node']['textfont']['size'] = self._configure_node_setting(node_text_font_size, 'text_font_size', self.conf['node']['textfont']['size'])

        self.conf['node']['marker']['size'] = self._configure_node_setting(node_size, 'size', self.conf['node']['marker']['size'])
        self.conf['node']['marker']['color'] = self._configure_node_setting(node_color, 'color', self.conf['node']['marker']['color'])
        self.conf['node']['marker']['opacity'] = self._configure_node_setting(node_opacity, None, self.conf['node']['marker']['opacity'])

        self.conf['node']['marker']['line']['width'] = self._configure_node_setting(node_border_width, 'line_size', self.conf['node']['marker']['line']['width'])
        self.conf['node']['marker']['line']['color'] = self._configure_node_setting(node_border_color, 'line_color', self.conf['node']['marker']['line']['color'])

        self.conf['edge']['width'] = self._configure_edge_setting(edge_width, 'width', self.conf['edge']['width'])
        self.conf['edge']['color'] = self._configure_edge_setting(edge_color, 'color', self.conf['edge']['color'])
        self.conf['edge']['opacity'] = self._configure_edge_setting(edge_opacity, None, self.conf['edge']['opacity'])
        self.conf['edge']['arrow']['show'] = self._configure_edge_setting(edge_arrow_show, 'arrow_show', self.conf['edge']['arrow']['show'])

        self.conf['edge']['textfont']['color'] = self._configure_edge_setting(edge_text_font_color, 'text_font_color', self.conf['edge']['textfont']['color'])
        self.conf['edge']['textfont']['family'] = self._configure_edge_setting(edge_text_font_family, 'text_font_family', self.conf['edge']['textfont']['family'])
        self.conf['edge']['textfont']['size'] = self._configure_edge_setting(edge_text_font_size, 'text_font_size', self.conf['edge']['textfont']['size'])
        self.conf['edge']['textoffset'] = self._configure_edge_setting(edge_text_offset, 'text_offset', self.conf['edge']['textoffset'])

    def _configure_node_setting(self, construct_param, attribute_name, current_setting):
        # convert list to dict (now, `current_setting` must be either a dict or a scalar value)
        if isinstance(current_setting, list):
            current_setting = dict(zip(self.nodes, current_setting))

        if construct_param is None:
            attribs = {}
            if attribute_name is not None:
                attribs = nx.get_node_attributes(self.G, attribute_name)
            if not attribs:
                # leave it as is
                return list(current_setting.values()) if isinstance(current_setting, dict) else current_setting
            else:
                # convert scalar to dict
                if not isinstance(current_setting, dict):
                    current_setting = {v: current_setting for v in self.nodes}
                current_setting.update(attribs)
                return list(current_setting.values())

        elif callable(construct_param):
            return [construct_param(v) for v in self.nodes]

        elif isinstance(construct_param, dict):
            attribs = {}
            if attribute_name is not None:
                attribs = nx.get_node_attributes(self.G, attribute_name)
            # convert scalar to dict
            if not isinstance(current_setting, dict):
                current_setting = {v: current_setting for v in self.nodes}
            current_setting.update(attribs)  # second priority
            current_setting.update(construct_param)  # first priority
            return list(current_setting.values())
        else:
            # set the given scalar value
            return construct_param

    def _configure_edge_setting(self, construct_param, attribute_name, current_setting):
        if construct_param is None:
            attribs = {}
            if attribute_name is not None:
                attribs = nx.get_edge_attributes(self.G, attribute_name)
            if not attribs:
                return current_setting
            else:
                # convert scalar to dict
                if not isinstance(current_setting, dict):
                    current_setting = {e: current_setting for e in self.edges}
                current_setting.update(attribs)
                return current_setting
        elif callable(construct_param):
            return {e: construct_param for e in self.edges}
        elif isinstance(construct_param, dict):
            attribs = {}
            if attribute_name is not None:
                attribs = nx.get_edge_attributes(self.G, attribute_name)
            # convert scalar to dict
            if not isinstance(current_setting, dict):
                current_setting = {e: current_setting for e in self.edges}
            current_setting.update(attribs)  # second priority
            current_setting.update(construct_param)  # first priority
            return current_setting
        else:
            return construct_param

    def _get_sub_setting(self, target, entity):
        return target[entity] if isinstance(target, dict) else target

    def _get_edge_traces(self, pos: Mapping[Vertex, Coord]):
        # group all edges by (color, width)
        groups = defaultdict(list)

        for edge in self.edges:
            if self._get_sub_setting(self.conf['edge']['arrow']['show'], edge):
                continue  # skip arrows
            color = self._get_sub_setting(self.conf['edge']['color'], edge)
            width = self._get_sub_setting(self.conf['edge']['width'], edge)
            groups[(color, width)] += [edge]

        # process each group
        is_3d = all(len(ps) == 3 for ps in pos.values())
        traces = []
        for (color, width), edges in groups.items():
            x, y, z = [], [], []
            for u, v in edges:
                x += [pos[u][0], pos[v][0], None]
                y += [pos[u][1], pos[v][1], None]
                if is_3d:
                    z += [pos[u][2], pos[v][2], None]

            params = dict(
                x=x,
                y=y,
                mode='lines',
                hoverinfo='none',
                line=dict(color=color, width=width),
                opacity=self.conf['edge']['opacity']
            )
            traces += [go.Scatter3d(z=z, **params) if is_3d else go.Scatter(**params)]

        return traces

    def _get_node_trace(self, pos: Mapping[Vertex, Coord]):
        xs = [list(t) for t in zip(*pos.values())]
        if len(xs) == 3:
            # 3D drawing if all positions are triples
            return go.Scatter3d(x=xs[0], y=xs[1], z=xs[2], **self.conf['node'])
        else:
            return go.Scatter(x=xs[0], y=xs[1], **self.conf['node'])

    def _get_arrow_annotations(self, pos: Mapping[Vertex, Coord]) -> List[go.layout.Annotation]:
        annotations = []
        for edge in self.edges:
            if self._get_sub_setting(self.conf['edge']['arrow']['show'], edge):
                u, v = edge

                def p(start: Tuple[float, float], end: Tuple[float, float], d: float):
                    """Returns the point distance-d away from v in line segment u-v."""
                    length = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
                    v_weight = (length - d) / length
                    u_weight = d / length
                    px = end[0] * v_weight + start[0] * u_weight
                    py = end[1] * v_weight + start[1] * u_weight
                    return px, py

                arrowhead = p(pos[u], pos[v], self._get_sub_setting(self.conf['edge']['arrow']['head_offset'], edge))
                arrowtail = p(pos[v], pos[u], self._get_sub_setting(self.conf['edge']['arrow']['tail_offset'], edge))

                annotations += [
                    go.layout.Annotation(
                        x=arrowhead[0],  # arrows' head
                        y=arrowhead[1],  # arrows' head
                        ax=arrowtail[0],  # arrows' tail
                        ay=arrowtail[1],  # arrows' tail
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        text='',  # if you want only the arrow
                        showarrow=True,
                        arrowhead=self.conf['edge']['arrow']['shape'],
                        arrowsize=self.conf['edge']['arrow']['size'],
                        arrowwidth=self._get_sub_setting(self.conf['edge']['width'], edge),
                        arrowcolor=self._get_sub_setting(self.conf['edge']['color'], edge),
                        opacity=self.conf['edge']['opacity']
                    )
                ]

        return annotations

    def _get_edge_text_annotations(self, pos: Mapping[Vertex, Coord]) -> List[go.layout.Annotation]:
        annotations = []
        for edge in self.edges:
            text = self._get_sub_setting(self.conf['edge']['text'], edge)
            if text:
                u, v = edge

                # interpret offset
                theta = math.atan2(pos[v][1] - pos[u][1], pos[v][0] - pos[u][0])
                offset = self._get_sub_setting(self.conf['edge']['textoffset'], edge)
                if isinstance(offset, tuple):
                    xshift, yshift = offset[0], offset[1]
                elif isinstance(offset, str):
                    if offset.startswith('cw('):
                        val = float(offset.replace('cw(', '').replace(')', ''))
                        xshift = val * math.cos(theta + math.pi / 2)
                        yshift = val * math.sin(theta + math.pi / 2)
                    elif offset.startswith('ccw('):
                        val = float(offset.replace('ccw(', '').replace(')', ''))
                        xshift = val * math.cos(theta - math.pi / 2)
                        yshift = val * math.sin(theta - math.pi / 2)
                    else:
                        raise ValueError(f'invalid edge textoffset: {offset}')
                else:
                    raise ValueError(f'invalid edge textoffset: {offset}')

                annotations += [
                    go.layout.Annotation(
                        x=(pos[v][0] + pos[u][0]) / 2,  # middle point
                        y=(pos[v][1] + pos[u][1]) / 2,
                        xshift=xshift,
                        yshift=yshift,
                        xref='x',
                        yref='y',
                        text=text,
                        showarrow=False,
                        font_color=self._get_sub_setting(self.conf['edge']['textfont']['color'], edge),
                        font_family=self._get_sub_setting(self.conf['edge']['textfont']['family'], edge),
                        font_size=self._get_sub_setting(self.conf['edge']['textfont']['size'], edge),
                    )
                ]
        return annotations

    def create_figure(self) -> go.Figure:
        axis_settings = dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            showline=False,
            visible=False,
            ticks='',
            showticklabels=False,
        )
        scene = dict(
            xaxis=axis_settings,
            yaxis=axis_settings,
            zaxis=axis_settings,
        )

        # determine node positions
        pos = nx.get_node_attributes(self.G, 'pos')
        if len(pos) != len(self.G):
            pos = nx.spring_layout(self.G)  # fall back to the Fruchterman-Reingold force-directed algorithm.

        annotations = self._get_arrow_annotations(pos) + self._get_edge_text_annotations(pos)
        fig = go.Figure(layout=go.Layout(xaxis=axis_settings, yaxis=axis_settings, scene=scene, annotations=annotations, **self.conf['layout']))
        fig.add_traces(self._get_edge_traces(pos))
        fig.add_trace(self._get_node_trace(pos))

        return fig

    def show(self) -> None:
        self.create_figure().show()

    def to_png(self, show=False) -> Any:
        ret = self.create_figure().to_image('png')
        if show:
            display(Image(ret))
            return
        return ret

    def to_jpg(self, show=False) -> Any:
        ret = self.create_figure().to_image('jpg')
        if show:
            display(Image(ret))
            return
        return ret

    def to_svg(self, show=False) -> Any:
        ret = self.create_figure().to_image('svg')
        if show:
            display(SVG(ret))
            return
        return ret

    def save(self, path: str, show: bool = False) -> None:
        self.create_figure().write_image(path)
        if show:
            if path.lower().endswith('.svg'):
                display(SVG(path))
            else:
                display(Image(path))
