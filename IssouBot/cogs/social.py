import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
import asyncio
import os
import time
import datetime

#Exclusive

class Social:
    """Extension sociale pour Discord."""

    def __init__(self, bot):
        self.bot = bot
        self.rift = dataIO.load_json("data/social/rift.json") #account
        self.settings = dataIO.load_json("data/social/settings.json")
        dft = {"ANNIV_SERV" : None, "ANNIV_CHAN" : None}

    @commands.group(pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def setrift(self, ctx):
        """Gestion de Rift."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @setrift.command(pass_context=True)
    async def server(self, ctx):
        """Permet de régler le serveur présent en tant que serveur de post."""
        server = ctx.message.server.id
        self.settings["ANNIV_SERV"] = server
        self.save()
        await self.bot.say("Effectué.")

    @setrift.command(pass_context=True)
    async def channel(self, ctx, channelid):
        """Permet de régler un channel en tant que channel de post."""
        self.settings["ANNIV_CHAN"] = channelid
        self.save()
        await self.bot.say("Effectué.")

    @setrift.command(pass_context=True)
    async def sync(self, ctx):
        """Force la synchronisation."""
        present = datetime.datetime.today().strftime("%d/%m")
        for id in self.rift:
            if self.rift[id]["NAISSANCE"] == present:
                server = self.settings["ANNIV_SERV"]
                server = self.bot.get_server(server)
                user = server.get_member(id)
                await self.bot.send_message(self.bot.get_channel(self.settings["ANNIV_CHAN"]), "**Joyeux anniversaire {} ! :gift:**".format(user.mention))
            else:
                pass
        else:
            await self.bot.say("Effectué.")

    @commands.group(pass_context=True)
    async def rft(self, ctx):
        """Commandes Rift."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @rft.command(pass_context=True)
    async def second(self, ctx, ident):
        """Permet de lier un secondaire au même profil en fournissant l'ID"""
        author = ctx.message.author
        if author.id in self.rift and ident in self.rift:
            if self.rift[ident]["SECONDAIRE"] == "Aucun" and self.rift[author.id]["SECONDAIRE"] == "Aucun":
                self.rift[ident]["SECONDAIRE"] = author.id
                self.rift[author.id]["SECONDAIRE"] = ident
                self.save()
                await self.bot.say("Comptes **{}** et **{}** liés !".format(author.name, self.rift[ident]["PSEUDO"]))
            else:
                await self.bot.say("Un des deux comptes a déjà un secondaire lié !")
        else:
            await self.bot.say("Un des deux comptes n'est pas inscrit sur Rift.")

    @rft.command(pass_context=True)
    async def delier(self, ctx):
        """Permet de délier un secondaire."""
        author = ctx.message.author
        if author.id in self.rift:
            if self.rift[author.id]["SECONDAIRE"] != "Aucun":
                sec = self.rift[author.id]["SECONDAIRE"]
                self.rift[author.id]["SECONDAIRE"] = "Aucun"
                self.rift[sec]["SECONDAIRE"] = "Aucun"
                self.save()
                await self.bot.say("Réalisé avec succès.")
            else:
                await self.bot.say("Aucun compte n'est lié au votre.")
        else:
            await self.bot.say("Vous n'êtes pas inscrit à Rift.")

    @rft.command(pass_context=True)
    async def inscr(self, ctx):
        """Permet de rejoindre Rift."""
        author = ctx.message.author
        ts = ctx.message.timestamp
        if author.id not in self.rift:
            await self.bot.whisper("**Salut {} !**\nBienvenue dans le réseau *Rift* !\nLe réseau *Rift* est une extension sociale que j'intègre pour combler les fonctionnalités proposées sur Discord.".format(author.name))
            await asyncio.sleep(1)
            await self.bot.whisper("**Nous allons configurer ton compte !**\n*Note: Tu peux ignorer toute question en tapant 'none'*")
            await asyncio.sleep(2)
            self.rift[author.id] = {"COMPLET" : str(author),
                                    "PSEUDO" : author.name,
                                    "ID" : author.id,
                                    "INSCRIPTION" : ts.strftime("%d/%m/%Y %H:%M:%S"),
                                    "NAISSANCE" : "Inconnu",
                                    "AGE" : "Inconnu",
                                    "PAYS" : "Inconnu",
                                    "REGION" : "Inconnue",
                                    "PROF" : "Inconnue",
                                    "COMPTES" : "Aucun",
                                    "COULEUR" : "0x607d8b",
                                    "DESC" : "Aucune",
                                    "SECONDAIRE" : "Aucun",
                                    "POP" : 0}

            chan = await self.bot.whisper("*Commençons.* Quel jour et mois es-tu né(e) ? (Format: *jj/mm*)")
            channel = chan.channel
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if "/" in rep.content:
                    if len(rep.content) == 5:
                        date = rep.content.split("/")
                        if int(date[0]) <= 31 and int(date[1]) <= 12:
                            await self.bot.whisper("**{}** Enregistré.\n\n".format(rep.content))
                            self.rift[author.id]["NAISSANCE"] = rep.content
                            self.save()
                            verif = True
                        else:
                            await self.bot.whisper("*Incorrect, recommence !*")
                    else:
                        await self.bot.whisper("*Incorrect, recommence !*")
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect, recommence !*")
            await asyncio.sleep(1)
            
            await self.bot.whisper("*Continuons.* Quel es ton âge ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if rep.content.isdigit():
                    await self.bot.whisper("**{}** Ans Enregistré.\n".format(rep.content))
                    self.rift[author.id]["AGE"] = int(rep.content)
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect, recommence !*")
            await asyncio.sleep(1)
            
            await self.bot.whisper("*Continuons.* Dans quel pays te trouves-tu ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["PAYS"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Dans quelle région de ce pays te trouves-tu ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["REGION"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Quelle est ta profession ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["PROF"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Veux-tu une couleur particulière pour ton profil ? Si oui, tu peux la rentrer sous la forme 0x<hex> (Tapes 'aide' pour avoir des exemples)")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if "0x" in rep.content:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["COULEUR"] = rep.content
                    self.save()
                    verif = True
                elif "aide" in rep.content.lower():
                    msg = "**__Exemples :__**\n"
                    msg += "*Noir* 0x000000\n"
                    msg += "*Bleu* 0x3446ce\n"
                    msg += "*Rouge* 0xce3434\n"
                    msg += "*Vert* 0x58ce34\n"
                    msg += "*Jaune* 0xccce34\n"
                    msg += "*Violet* 0xce34c7\n"
                    await self.bot.whisper(msg)
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Couleur non reconnue, le format doit être '0x' suivi de la couleur en hexadecimal)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Voudrais-tu donner une description rapide de toi ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("Description enregistrée.\n".format(rep.content))
                    self.rift[author.id]["DESC"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Presque terminé !* Voudrais-tu afficher des comptes de différentes plateformes ?\nSi oui, tu peux les rentrer sous cette forme: *Snap:Toncompte/Steam:Toncompte/(etc...)*")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                comptes = []
                if len(rep.content) >= 5:
                    poss = rep.content.split("/")
                    for c in poss:
                        d = c.split(":")
                        comptes.append([d[0],d[1]])
                    await self.bot.whisper("**Comptes enregistrés**\n".format(rep.content))
                    self.rift[author.id]["COMPTES"] = comptes
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Le format n'est pas bon)*")
            await asyncio.sleep(1)
            await self.bot.whisper("**Terminé !** Tu peux vérifier ton compte avec [p]rft profil")
        else:
            await self.bot.say("*Tu es déjà inscrit !*")

    @rft.command(pass_context=True) #REINSCRIPTION
    async def reinscr(self, ctx):
        """Permet de refaire son compte Rift."""
        author = ctx.message.author
        ts = ctx.message.timestamp
        if author.id in self.rift:
            await self.bot.whisper("**Salut {} !**\nNous allons reconfigurer ton compte Rift !".format(author.name))
            await asyncio.sleep(1)
            await self.bot.whisper("*Tu peux toujours ignorer une question en tapant 'none' à la place de la réponse.*")
            await asyncio.sleep(2)
            self.rift[author.id] = {"COMPLET" : str(author),
                                    "PSEUDO" : author.name,
                                    "ID" : author.id,
                                    "INSCRIPTION" : ts.strftime("%d/%m/%Y %H:%M:%S"),
                                    "NAISSANCE" : "Inconnu",
                                    "AGE" : "Inconnu",
                                    "PAYS" : "Inconnu",
                                    "REGION" : "Inconnue",
                                    "PROF" : "Inconnue",
                                    "COMPTES" : "Aucun",
                                    "COULEUR" : "0x607d8b",
                                    "DESC" : "Aucune",
                                    "SECONDAIRE" : "Aucun",
                                    "POP" : 0}

            chan = await self.bot.whisper("*Commençons.* Quel jour et mois es-tu né(e) ? (Format: *jj/mm*)")
            channel = chan.channel
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if "/" in rep.content:
                    if len(rep.content) == 5:
                        date = rep.content.split("/")
                        if int(date[0]) <= 31 and int(date[1]) <= 12:
                            await self.bot.whisper("**{}** Enregistré.\n\n".format(rep.content))
                            self.rift[author.id]["NAISSANCE"] = rep.content
                            self.save()
                            verif = True
                        else:
                            await self.bot.whisper("*Incorrect, recommence !*")
                    else:
                        await self.bot.whisper("*Incorrect, recommence !*")
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect, recommence !*")
            await asyncio.sleep(1)
            
            await self.bot.whisper("*Continuons.* Quel es ton âge ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if rep.content.isdigit():
                    await self.bot.whisper("**{}** Ans Enregistré.\n".format(rep.content))
                    self.rift[author.id]["AGE"] = int(rep.content)
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect, recommence !*")
            await asyncio.sleep(1)
            
            await self.bot.whisper("*Continuons.* Dans quel pays te trouves-tu ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["PAYS"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Dans quelle région de ce pays te trouves-tu ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["REGION"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Quelle est ta profession ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["PROF"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Veux-tu une couleur particulière pour ton profil ? Si oui, tu peux la rentrer sous la forme 0x<hex> (Tapes 'aide' pour avoir des exemples)")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if "0x" in rep.content:
                    await self.bot.whisper("**{}** Enregistré.\n".format(rep.content))
                    self.rift[author.id]["COULEUR"] = rep.content
                    self.save()
                    verif = True
                elif "aide" in rep.content.lower():
                    msg = "**__Exemples :__**\n"
                    msg += "*Noir* 0x000000\n"
                    msg += "*Bleu* 0x3446ce\n"
                    msg += "*Rouge* 0xce3434\n"
                    msg += "*Vert* 0x58ce34\n"
                    msg += "*Jaune* 0xccce34\n"
                    msg += "*Violet* 0xce34c7\n"
                    await self.bot.whisper(msg)
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Couleur non reconnue, le format doit être '0x' suivi de la couleur en hexadecimal)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Continuons.* Voudrais-tu donner une description rapide de toi ?")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                if len(rep.content) >= 5:
                    await self.bot.whisper("Description enregistrée.\n".format(rep.content))
                    self.rift[author.id]["DESC"] = rep.content
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Au moins 5 caractères minimum)*")
            await asyncio.sleep(1)

            await self.bot.whisper("*Presque terminé !* Voudrais-tu afficher des comptes de différentes plateformes ?\nSi oui, tu peux les rentrer sous cette forme: *Snap:Toncompte/Steam:Toncompte/(etc...)*")
            verif = False
            while verif != True:
                rep = await self.bot.wait_for_message(author=author, channel=channel)
                comptes = []
                if len(rep.content) >= 5:
                    poss = rep.content.split("/")
                    for c in poss:
                        d = c.split(":")
                        comptes.append([d[0],d[1]])
                    await self.bot.whisper("**Comptes enregistrés**\n".format(rep.content))
                    self.rift[author.id]["COMPTES"] = comptes
                    self.save()
                    verif = True
                elif "none" in rep.content.lower():
                    await self.bot.whisper("**Ignoré.**")
                    verif = True
                else:
                    await self.bot.whisper("*Incorrect (Le format n'est pas bon)*")
            await asyncio.sleep(1)
            await self.bot.whisper("**Voilà !** Tu peux vérifier ton compte avec [p]rft profil")
        else:
            await self.bot.say("*Tu n'es pas inscrit !*")

    @rft.command(pass_context=True)
    async def profil(self, ctx, user: discord.Member = None):
        """Permet de voir le profil Rift d'un utilisateur."""
        author = ctx.message.author
        if user == None:
            user = author
        if user.id in self.rift:
            coul = self.rift[user.id]["COULEUR"]
            coul = int(coul, 16)
            em = discord.Embed(title="A propos de {}".format(str(user)), colour=coul, inline=False)
            em.add_field(name="Pseudo", value = str(user.display_name))
            em.add_field(name="ID", value = str(user.id))
            em.add_field(name="Anniversaire", value = str(self.rift[user.id]["NAISSANCE"]))
            em.add_field(name="Age", value = str(self.rift[user.id]["AGE"]))
            em.add_field(name="Pays/Region", value = "{}/{}".format(self.rift[user.id]["PAYS"],self.rift[user.id]["REGION"]))
            em.add_field(name="Popularité" , value = "{}pp".format(self.rift[user.id]["POP"]))
            em.add_field(name="Description", value = self.rift[user.id]["DESC"])
            em.add_field(name="Profession", value = str(self.rift[user.id]["PROF"]))
            comptes = self.rift[user.id]["COMPTES"]
            msg = ""
            if self.rift[user.id]["COMPTES"] != "Aucun":
                for e in comptes:
                    msg += "{}: {}\n".format(e[0],e[1])
            else:
                msg = "Aucun"
            em.add_field(name="Comptes", value= msg)
            em.set_image(url=user.avatar_url)
            em.set_footer(text="Inscrit le {}".format(self.rift[user.id]["INSCRIPTION"]))
            await self.bot.whisper(embed=em)
        else:
            await self.bot.whisper("L'utilisateur n'est pas inscrit sur Rift")

    @rft.command(pass_context=True, hidden=True)
    async def suppr(self, ctx, user: discord.Member = None):
        """Permet la reinitialisation d'un compte Rift."""
        if user.id in self.rift:
            del self.rift[user.id]
            await self.bot.say("Effectué avec succès.")
            self.save()
        else:
            await self.bot.say("Impossible")

    async def checking(self):
        while self == self.bot.get_cog("Social"):
            if self.settings["ANNIV_SERV"] != None:
                present = datetime.datetime.today().strftime("%d/%m")
                for id in self.rift:
                    server = self.settings["ANNIV_SERV"]
                    server = self.bot.get_server(server)
                    user = server.get_member(id)
                    if self.rift[id]["PSEUDO"] != user.name:
                        self.rift[id]["PSEUDO"] = user.name
                        self.save()
                    if self.rift[id]["NAISSANCE"] == present:
                        await self.bot.send_message(self.settings["ANNIV_CHAN"], "**Joyeux anniversaire {} ! :gift:**".format(user.mention))
                        self.rift[id]["AGE"] += 1
                        self.save()
                    else:
                        pass
            else:
                pass
            await asyncio.sleep(86400) #24h entre chaque verification

    async def pop(self, message):
        author = message.author
        mentions = message.mentions
        if mentions != []:
            for member in mentions:
                for id in self.rift:
                    if member.id == self.rift[id]["ID"]:
                        if member.id != author.id:
                            self.rift[id]["POP"] += 1
                            self.save()
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        for id in self.rift:
            if self.rift[id]["PSEUDO"].lower() in message.content.lower():
                if author.id != id:
                    self.rift[id]["POP"] += 1
                    self.save()
                else:
                    pass
            else:
                pass

    def save(self):
        fileIO("data/social/rift.json", "save", self.rift)
        fileIO("data/social/settings.json", "save", self.settings)
        return True

def check_folders():
    if not os.path.exists("data/social"):
        print("Creation du dossier de stockage Social...")
        os.makedirs("data/social")

def check_files():
    if not os.path.isfile("data/social/rift.json"):
        print("Creation du fichier de comptes Rift...")
        fileIO("data/social/rift.json", "save", {})

    if not os.path.isfile("data/social/settings.json"):
        print("Creation du fichier de paramètres Rift...")
        fileIO("data/social/settings.json", "save", dft)

def setup(bot):
    check_folders()
    check_files()
    n = Social(bot)
    bot.loop.create_task(n.checking())
    bot.add_listener(n.pop, "on_message")
    bot.add_cog(n)
