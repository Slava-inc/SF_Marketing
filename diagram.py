import os
import matplotlib.pyplot as plt


class UserCosts:

    @staticmethod
    async def create_diagram_outlay(costs_name: list, costs_value: list):
        fig1, ax1 = plt.subplots()
        ax1.pie(costs_value, labels=costs_name, autopct='%1.1f%%')
        if not os.path.exists("images"):
            os.mkdir("images")
        plt.savefig("images/fig1.png")
        return True
