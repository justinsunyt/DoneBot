import discord
import discord.utils


# insert bot token below
token = ""
tasks = {}
scores = {}


# shop for custom roles (format - "role": price)
shop = {
    "Copper": 1, "Bronze": 10, "Silver": 50, "Gold": 100, "Platinum": 500, "Diamond": 1000, "Champion": 10000
}


client = discord.Client()


# updates data.txt with users' tasks and scores
def update_data():
    global tasks
    print(tasks)
    try:
        with open("data.txt", "w") as f:
            for user in tasks:
                for task in tasks[user]:
                    f.write("//task//" + str(user) + ":::" + str(task) + "\n")
            for user in scores:
                f.write("//score//" + str(user) + ":::" + str(scores[user]) + "\n")
    except Exception as e:
        print(e)


# adds task to tasks and calls update_data()
def add_task(user, task):
    global tasks
    if user not in tasks:
        tasks[user] = []
    tasks[user].append(task)
    print(user, tasks[user])
    update_data()


# deletes task from tasks; returns True if task can be found, calls update_data(), False if not
def del_task(user, task):
    global tasks
    if user in tasks:
        if task in tasks[user]:
            tasks[user].remove(task)
            update_data()
            return True
    return False


# adds score to scores and calls update_data()
def add_score(user):
    global scores
    if user not in scores:
        scores[user] = 0
    scores[user] += 1
    print(user, scores[user])
    update_data()


# gets tasks from data.txt
def get_tasks():
    global tasks
    try:
        f = open("data.txt", "r")
        lines = f.readlines()
        for line in lines:
            if line.startswith("//task//"):
                user, task = line[8:].split(":::")
                if user not in tasks:
                    tasks[user] = []
                tasks[user].append(task[:-1])
        f.close()
    except Exception as e:
        print(e)
    print(tasks)


# gets scores from data.txt
def get_scores():
    global scores
    try:
        f = open("data.txt", "r")
        lines = f.readlines()
        for line in lines:
            if line.startswith("//score//"):
                user, score = line[9:].split(":::")
                scores[user] = int(score[:-1])
        f.close()
    except Exception as e:
        print(e)
    print(scores)


# checks if items can be bought, and if so, deducts points (item's cost) from user
def buy_item(user, item):
    global shop
    global scores
    if item not in shop:
        return False
    elif user in scores:
        if scores[user] < shop[item]:
            return False
        else:
            scores[user] -= shop[item]
            update_data()
            return True
    else:
        return False


@client.event
async def on_ready():
    get_tasks()
    get_scores()


@client.event
async def on_message(message):
    # available channels for bot
    channels = ["bots", "donebot"]

    if str(message.channel) in channels:
        # !hello
        if message.content == "!hello":
            await message.channel.send("Hi! If you need help, type !help")
        # !help
        elif message.content == "!help":
            await message.channel.send('''Type "!add" to add task, "!del" to delete task, "!done" to mark a task as completed''')
            await message.channel.send('''"!tasks" to check uncompleted tasks, and "!score" to check your score''')
        # !add
        elif message.content.startswith("!add"):
            add_task(str(message.author), message.content[5:])
            await message.channel.send("Task added")
        # !del
        elif message.content.startswith("!del"):
            if del_task(str(message.author), message.content[5:]):
                await message.channel.send("Task deleted")
            else:
                await message.channel.send("Task not found")
        # !done
        elif message.content.startswith("!done"):
            if del_task(str(message.author), message.content[6:]):
                await message.channel.send("Task done")
                add_score(str(message.author))
                await message.channel.send("Your score is: " + str(scores[str(message.author)]))
            else:
                await message.channel.send("Task not found")
        # !tasks
        elif message.content == ("!tasks"):
            if not tasks:
                await message.channel.send("No tasks found")
            elif str(message.author) not in tasks:
                await message.channel.send("No tasks found")
            else:
                for user in tasks:
                    if str(message.author) == user:
                        for task in tasks[user]:
                            await message.channel.send(task)
        # !score
        elif message.content == ("!score"):
            if not scores:
                await message.channel.send("No scores found")
            elif str(message.author) not in scores:
                await message.channel.send("No scores found")
            else:
                await message.channel.send("Your score is: " + str(scores[str(message.author)]))
        # !shop
        elif message.content == ("!shop"):
            for item in shop:
                await message.channel.send("Item: " + item + ", Price = " + str(shop[item]))
        # !shop
        elif message.content.startswith("!buy"):
            item = message.content[5:].lower().capitalize()
            if not buy_item(str(message.author), item):
                await message.channel.send("Not enough points")
            else:
                await message.channel.send("Item purchased!")
                for it in shop:
                    if it == item:
                        role = discord.utils.get(message.guild.roles, name = item)
                await message.author.add_roles(role)


client.run(token)