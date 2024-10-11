import plotly.graph_objects as go
from dispatcher import Dispatcher as dp
from aiogram import types

class UserCosts:
    def __init__(self, costs_list, costs_value):
        self.costs_list = costs_list
        self.costs_value = costs_value

@dp.message_handler(command=['analyze'])
async def create_diagram(message:types.Message):
    cost_list = ['еда', 'транспорт', 'мебель', 'жкх', 'связь', 'другое']
    cost_value = [ 15000, 1000, 2000, 3000, 1000, 4000]
    user = UserCosts(cost_list, cost_value)
    fig = go.Figure(data=[go.Pie(labels=user.costs_list, values=user.costs_value)])
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20)
    await message.reply(message.chat.id, fig.show())
