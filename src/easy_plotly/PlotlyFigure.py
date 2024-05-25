import copy
from typing import List, Mapping, Union, Any
import yaml
import plotly.graph_objects as go
import plotly.subplots
from IPython.display import display, Image, SVG


class PlotlyFigure:
    def __init__(self, config_path: str = None, title: str = None, x_title: str = None, y_title: str = None, rows: int = 1, cols: int = 1, **subplots_options) -> None:
        if config_path is None:
            self.conf = {
                'layout': {
                    'xaxis': {'title': {'text': 'X_TITLE'}},
                    'yaxis': {'title': {'text': 'Y_TITLE'}}
                }
            }
        else:
            with open(config_path, 'r') as f:
                self.conf = yaml.safe_load(f)

        # create figure
        if rows == 1 and cols == 1:
            self.fig = go.Figure()
        else:
            self.fig = plotly.subplots.make_subplots(rows=rows, cols=cols, **subplots_options)
            if 'subplot_title' in self.conf['layout']:
                self.fig.update_annotations(**self.conf['layout']['subplot_title'])
                del self.conf['layout']['subplot_title']

        # overwrite titles
        if title is not None:
            self.conf['layout']['title']['text'] = title  # optional
        if x_title is not None:
            self.conf['layout']['xaxis']['title']['text'] = x_title
        if y_title is not None:
            self.conf['layout']['yaxis']['title']['text'] = y_title

        # update styles
        self.fig.update_layout(self.conf['layout'])

    def add_scatter(
        self,
        x: List[float],
        y: List[float],
        name: str = None,
        text: List[str] = None,
        template: Union[str, int, float] = None,
        row: int = None,
        col: int = None,
        **params,
    ) -> go.Figure:
        return self.__add_trace(go.Scatter, template, row, col, x=x, y=y, name=name, text=text, **params)

    def add_bar(
        self,
        x: List[float],
        y: List[float],
        name: str = None,
        text: List[str] = None,
        template: Union[str, int, float] = None,
        row: int = None,
        col: int = None,
        **params,
    ) -> go.Figure:
        return self.__add_trace(go.Bar, template, row, col, x=x, y=y, name=name, text=text, **params)

    def add_box(
        self,
        x: List[float],
        y: List[float],
        name: str = None,
        text: List[str] = None,
        template: Union[str, int, float] = None,
        row: int = None,
        col: int = None,
        **params,
    ) -> go.Figure:
        return self.__add_trace(go.Box, template, row, col, x=x, y=y, name=name, text=text, **params)

    def add_violin(
        self,
        x: List[float],
        y: List[float],
        name: str = None,
        text: List[str] = None,
        template: Union[str, int, float] = None,
        row: int = None,
        col: int = None,
        **params,
    ) -> go.Figure:
        return self.__add_trace(go.Violin, template, row, col, x=x, y=y, name=name, text=text, **params)

    def __add_trace(
        self,
        trace_obj: Any,
        template: Union[str, int, float] = None,
        row: int = None,
        col: int = None,
        **params
    ) -> go.Figure:
        subplots_params = {}
        if row is not None and col is not None:
            subplots_params = dict(row=row, col=col)

        self.fig.add_trace(trace_obj(
            **params,
            **self.__get_trace_params(template)
        ), **subplots_params)

        return self.fig

    def show(self) -> None:
        self.fig.show()

    def to_png(self, show=False) -> Any:
        ret = self.fig.to_image('png')
        if show:
            display(Image(ret))
            return
        return ret

    def to_jpg(self, show=False) -> Any:
        ret = self.fig.to_image('jpg')
        if show:
            display(Image(ret))
            return
        return ret

    def to_svg(self, show=False) -> Any:
        ret = self.fig.to_image('svg')
        if show:
            display(SVG(ret))
            return
        return ret

    def save(self, path: str, show: bool = False) -> None:
        self.fig.write_image(path)
        if show:
            if path.lower().endswith('.svg'):
                display(SVG(path))
            else:
                display(Image(path))

    def __get_trace_params(self, template: Union[str, int, float]) -> Mapping[str, Any]:
        return self.__update_nested_dict(self.conf['traces']['default'], self.conf['traces'].get(template))

    def __update_nested_dict(self, d: Mapping, other: Mapping) -> Mapping:
        ret = copy.deepcopy(d)

        if other is not None:
            self.__update_nested_dict_rec(ret, other)
        return ret

    def __update_nested_dict_rec(self, d: Mapping, other: Mapping) -> Mapping:
        """Helper function for updating nested dictionaries."""

        for k, v in other.items():
            if isinstance(v, dict):
                d[k] = d.get(k, {})
                self.__update_nested_dict_rec(d[k], v)
            else:
                d[k] = v
