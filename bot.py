from typing import Any
from discord.ext import commands
import discord
import services
from allowedCategories import AllowedCategories
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
REQUIRED_PERMISSIONS = discord.Permissions(administrator=True)
BOT_TOKEN = os.environ['BOT_TOKEN']


class ChooseFilterCategories(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category, value=category) for category in AllowedCategories.badWordsCategories
        ]

        super().__init__(options=options, placeholder="Choose categories to blur words",max_values=len(AllowedCategories.badWordsCategories) - 1)

    async def callback(self, interaction):
        await self.view.choosenCategoriesRespond(interaction, self.values)

class FilterCategoryView(discord.ui.View):
    answer = None
    choosenCategories = None

    @discord.ui.select(
        placeholder="With what categories words should be blured",
        options=[
            discord.SelectOption(label='Every category', value='every'),
            discord.SelectOption(label='Choose some categories', value='choose'),
        ]
    )
    async def select_age(self, interaction: discord.Integration, select_item: discord.ui.Select):
        self.answer = select_item.values
        self.children[0].disabled = True
        if self.answer[0] != 'every':
            categoriesSelect = ChooseFilterCategories()
            self.add_item(categoriesSelect)

        await interaction.message.edit(view=self)
        await interaction.response.defer()
        if self.answer[0] == 'every':
            self.stop()

    async def choosenCategoriesRespond(self, interaction: discord.Integration, choices):
        self.choosenCategories = choices
        await interaction.response.defer()
        self.stop()    

async def set_categories(ctx):
    user = ctx.author
    admin_role = await services.is_admin_role(user, REQUIRED_PERMISSIONS)
    
    if admin_role:
        allowed_categories = AllowedCategories(ctx.guild.id)

        allowed_categories.clear()
        view = FilterCategoryView()
        await ctx.author.send(view=view)

        await view.wait()
        if view.answer[0] == 'choose':
            for c in view.choosenCategories:
                allowed_categories.pushCategory(c)
                
    else:
        await ctx.send("Admin role not found.")


async def set_filter_settings(message):
    user = message.author
    admin_role = await services.is_admin_role(user, REQUIRED_PERMISSIONS)
    
    if admin_role:
        select = discord.ui.Select(
            placeholder="Choose what messages should be filter",
            options = [
                discord.SelectOption(label='Filter hate and offensive messages', value='filterHate'),
                discord.SelectOption(label='Filter scam messages', value='filterScam'),
                discord.SelectOption(label='Filter spam messages', value='filterSpam'),
                discord.SelectOption(label='Blur hate and offensive messages images', value='blurHateImages')
            ],
            max_values=4
        )

        async def filterSelectCallback(interaction):
            answer = {
                "filterHate": "filterHate" in select.values,
                "filterScam": "filterScam" in select.values,
                "filterSpam": "filterSpam" in select.values,
                "blurHateImages": "blurHateImages" in select.values
            }
            allowed_categories = AllowedCategories(message.guild.id)
            allowed_categories.setSettings(answer)
            await interaction.response.defer()

        select.callback = filterSelectCallback
        view = discord.ui.View()
        view.add_item(select)
        await user.send("Choose what messages should be filter", view=view)

    else:
        await message.send("Admin role not found.")

@bot.event
async def on_message(message):
    if (message.author == bot.user):
        return

    allowed_categories = AllowedCategories(message.guild.id)
    settings = allowed_categories.getSettings()

    if (message.attachments):
        #image hate check and blur
        if settings['blurHateImages']:
            await services.imageHateCheck(message)

    if (message.content):
        #hate check and blur / delete
        if settings['filterHate']:
            await services.hateCheck(message)

        #scam check
        if settings['filterScam']:
            await services.scamCheck(message)

        #spam check
        if settings['filterSpam']:
            await services.spamCeck(message)

    if (message.content.startswith('!set_categories')):
        await set_categories(message)

    if (message.content.startswith('!set_filter_settings')):
        await set_filter_settings(message)



bot.run(BOT_TOKEN)
