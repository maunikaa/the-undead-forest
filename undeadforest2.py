import os
import asyncio
import sqlite3
import random
import datetime
import re
import math
import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from dotenv import load_dotenv

# TODO:
# - set up multiple img slots for claim cmd
# - add admin cmd to 

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


# ============================================================
# Locations
# ============================================================

LOCATIONS = [
    {
        "id": "abandoned-cabin",
        "name": "The Abandoned Cabin",
        "story": "The trees have grown thick around an old wooden cabin. Its windows are dark, the door hangs slightly open, and something inside makes a quiet scratching sound.",
        "command": "cabin",
        "prompts": [
            {
                "id": "Cabin Prompt 1",
                "text": "Read a book you’ve been putting off",
                "points": 100
            },
            {
                "id": "Cabin Prompt 2",
                "text": "Finish a book you nearly DNFed",
                "points": 100
            },
            {
                "id": "Cabin Prompt 3",
                "text": "Participate in 2 sprints",
                "points": 100
            },
        ],
    },
    {
        "id": "halloween-town",
        "name": "Halloween Town",
        "story": "Orange lights flicker between abandoned storefronts as fog rolls through the empty streets. Jack-o'-lanterns grin from every doorstep. You hear footsteps behind you. When you turn around... nothing is there.",
        "command": "town",
        "prompts": [
            {
                "id": "Town Prompt 1",
                "text": "Read and log a book with a cover that’s warm toned",
                "points": 200
            },
            {
                "id": "Town Prompt 2",
                "text": "Share a halloween song that reminds you of a book you logged",
                "points": 200
            },
            {
                "id": "Town Prompt 3",
                "text": "Make a halloween moodboard for a logged book (the book doesn’t need to match entirely, the vibes matter!)",
                "points": 200
            },
        ],        
    },
    {
        "id": "tower-of-terror",
        "name": "The Tower of Terror",
        "story": "The tower rises above the treeline, disappearing into the clouds. The elevator doors open by themselves. No one is inside. But the button for the top floor has already been pressed.",
        "command": "tower",
        "prompts": [
            {
                "id": "Tower Prompt 1",
                "text": "Read 100 pages of a horror book after getting a mod to agree to hold your hand through it",
                "points": 300
            },
            {
                "id": "Tower Prompt 2",
                "text": "Read 100 pages of a thriller book while in a sprint",
                "points": 300
            },
            {
                "id": "Tower Prompt 3",
                "text": "Read and log a 100+ page mystery book",
                "points": 300
            },
        ],  
    },
    {
        "id": "trick-or-treat-trail",
        "name": "The Trick or Treat Trail",
        "story": "A trail of glowing pumpkins winds deeper into the forest. Candy wrappers crunch beneath your feet. At the end of the path sits a basket filled with treats. There's only one problem. You don't remember putting it there.",
        "command": "trail",
        "prompts": [
            {
                "id": "Trail Prompt 1",
                "text": "Read a book recommended to you",
                "points": 400
            },
            {
                "id": "Trail Prompt 2",
                "text": "Write a nice review about a book (three sentences minimum)",
                "points": 400
            },
            {
                "id": "Trail Prompt 3",
                "text": "Write a critical review about a book (three sentences minimum)",
                "points": 400
            },
            {
                "id": "Trail Prompt 4",
                "text": "Have someone choose the book you read from three options with each one being from a different genre",
                "points": 400
            },
            {
                "id": "Trail Prompt 5",
                "text": "Read and log a book with something sweet on the cover",
                "points": 400
            },
        ],  
    },
    {
        "id": "final-girl-hideout",
        "name": "The Final Girl Hideout",
        "story": "You find a hidden room tucked beneath an old hunting lodge. Maps cover the walls. Supplies are stacked neatly in the corner. Whoever built this place knew exactly what they were doing. Maybe you finally found somewhere safe.",
        "command": "hideout",
        "prompts": [
            {
                "id": "Hideout Prompt 1",
                "text": "Participate in five sprints",
                "points": 500
            },
            {
                "id": "Hideout Prompt 2",
                "text": "Share your favorite female character and explain why you gravitate towards them",
                "points": 500
            },
            {
                "id": "Hideout Prompt 3",
                "text": "Read a book with a strong female lead",
                "points": 500
            },
            {
                "id": "Hideout Prompt 4",
                "text": "Finish and log 3 new books",
                "points": 500
            },
            {
                "id": "Hideout Prompt 5",
                "text": "Read a book with a major plot twist",
                "points": 500
            },
        ],  
    },
    {
        "id": "haunted-cemetery",
        "name": "The Haunted Cemetery",
        "story": "The trees suddenly open into a forgotten cemetery. Crooked headstones disappear into the fog, and candles flicker beside graves that look far too recently disturbed. Somewhere among the tombstones, you hear your name whispered.",
        "command": "cemetery",
        "prompts": [
            {
                "id": "Cemetery Prompt 1",
                "text": "Read a paranormal book recommended by a mod",
                "points": 600
            },
            {
                "id": "Cemetery Prompt 2",
                "text": "Read and log a book with ghosts (minimum 200 pages)",
                "points": 600
            },
            {
                "id": "Cemetery Prompt 3",
                "text": "Do six hours worth of sprints while reading a paranormal book",
                "points": 600
            },
            {
                "id": "Cemetery Prompt 4",
                "text": "For thirty minutes, hang out with a mod in VC and listen to scary sounds",
                "points": 600
            },
            {
                "id": "Cemetery Prompt 5",
                "text": "Read 200 pages of a classic gothic book",
                "points": 600
            },
        ],  
    },
    {
        "id": "creature's-lair",
        "name": "The Creature's Lair",
        "story": "You stumble into a massive cavern hidden beneath the forest floor. Strange footprints cover the ground. They aren't human. And judging by the size of them... whatever made them is still nearby.",
        "command": "lair",
        "prompts": [
            {
                "id": "Lair Prompt 1",
                "text": "Participate in five evening sprints in your time zone that lasted an hour minimum",
                "points": 700
            },
            {
                "id": "Lair Prompt 2",
                "text": "Read a book where vampires and humans co-exist",
                "points": 700
            },
            {
                "id": "Lair Prompt 3",
                "text": "Read and log a book where its universe contains three species or more",
                "points": 700
            },
            {
                "id": "Lair Prompt 4",
                "text": "Have a friendly debate with a grove member about which monster would be better as a companion",
                "points": 700
            },
            {
                "id": "Lair Prompt 5",
                "text": "Read a book where a human falls in love with a monstrous character",
                "points": 700
            },
            {
                "id": "Lair Prompt 6",
                "text": "Create a team of six fictional characters that you would trust to monster hunt with you",
                "points": 700
            },
            {
                "id": "Lair Prompt 7",
                "text": "Pick a creature from a book you’ve logged and explain why their actions make them belong in the creature’s lair",
                "points": 700
            },
        ],  
    },
    {
        "id": "festival-grounds",
        "name": "The Festival Grounds",
        "story": "Music drifts through the trees. Ahead, lanterns illuminate a celebration unlike anything you've seen before. People gather in costumes, sharing food, stories, and traditions passed down through generations. For the first time in the forest, you don't feel alone.",
        "command": "festival",
        "prompts": [
            {
                "id": "Festival Prompt 1",
                "text": "Read a book where halloween is disliked by character, explain their reasoning and whether you think it’s valid or not",
                "points": 800
            },
            {
                "id": "Festival Prompt 2",
                "text": "Read and log a book that’s worth five stars to you and include why in your submission (minimum three sentences)",
                "points": 800
            },
            {
                "id": "Festival Prompt 3",
                "text": "Read and log a 300+ page book with only orange, white and black on the cover",
                "points": 800
            },
            {
                "id": "Festival Prompt 4",
                "text": "Read and log a book that has a playlist in it which includes ten songs or more",
                "points": 800
            },
            {
                "id": "Festival Prompt 5",
                "text": "Create an ensemble of magical fictional characters to star as the main acts in your circus (five characters minimum, more than that is appreciated)",
                "points": 800
            },
            {
                "id": "Festival Prompt 6",
                "text": "Name five grove members you’d want to see as acts in a circus, explain why and what they would do and which one would be the final act",
                "points": 800
            },
            {
                "id": "Festival Prompt 7",
                "text": "Share three songs you’d perform with no shame to the festival grounds audience and include hypothetical outfit(s)",
                "points": 800
            },
        ],  
    },    
]

LOCATION_MAP = {loc["id"]: loc for loc in LOCATIONS}
LOCATION_ORDER = [loc["id"] for loc in LOCATIONS]


# ============================================================
# Database Setup
# ============================================================

DB_FILE = "undead_forest.db"

def get_db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def setup_db():
    connection = get_db()
    cursor = connection.cursor()
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                       user_id INTEGER PRIMARY KEY,
                       current_location_idx INTEGER NOT NULL DEFAULT 0,
                       points INTEGER NOT NULL DEFAULT 0
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS active_prompts (
                       user_id INTEGER NOT NULL,
                       location_id TEXT NOT NULL,
                       prompt_id TEXT NOT NULL,
                       PRIMARY KEY (user_id, location_id, prompt_id)
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS completed_prompts (
                       user_id INTEGER NOT NULL,
                       location_id TEXT NOT NULL,
                       prompt_id TEXT NOT NULL,
                       proof_url TEXT NOT NULL,
                       points INTEGER NOT NULL,
                       PRIMARY KEY (user_id, location_id, prompt_id)
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS pending_claims (
                       message_id INTEGER PRIMARY_KEY,
                       user_id INTEGER NOT NULL,
                       location_id TEXT NOT NULL,
                       prompt_id TEXT NOT NULL,
                       proof_urls TEXT NOT NULL,
                       points INTEGER NOT NULL
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS books (
                       id INTEGER PRIMARY_KEY,
                       user_id INTEGER NOT NULL,
                       title TEXT NOT NULL,
                       author TEXT NOT NULL,
                       page_count INTEGER NOT NULL,
                       rating INTEGER,
                       points INTEGER NOT NULL,
                       logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS server_settings (
                       guild_id INTEGER PRIMARY_KEY,
                       submission_channel_id INTEGER,
                       response_channel_id INTEGER
                   )
                   """)
    connection.commit()
    connection.close()


# ============================================================
# Database Helper Functions
# ============================================================

def sync_get_user_stats(user_id: int) -> tuple[int, int]:
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT current_location_idx, points FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()  
    if row:
        return row[0], row[1]
    cursor.execute("INSERT INTO users (user_id, current_location_idx, points) VALUES (?, 0, 0)", (user_id,))
    connection.commit()
    connection.close()
    return 0,0

def sync_get_profile_data(user_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT current_location_idx, points FROM users WHERE user_id=?", (user_id,))
    user_row = cursor.fetchone() or (0,0)
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(page_count), 0) FROM books WHERE user_id=?", (user_id,))
    book_row = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM completed_prompts WHERE user_id=?", (user_id,))
    prompts_completed = cursor.fetchone()[0]
    return user_row[0], user_row[1], book_row[0], book_row[1], prompts_completed

def sync_get_prompt_statuses(user_id: int, location_id: str):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT prompt_id FROM active_prompts WHERE user_id=? AND location_id=?", (user_id, location_id))
    active = {row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT prompt_id FROM completed_prompts WHERE user_id=? AND location_id=?", (user_id, location_id))
    completed = {row[0] for row in cursor.fetchall()}
    return active, completed

def sync_add_active_prompt(user_id: int, location_id: str, prompt_id: str):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO active_prompts (user_id, location_id, prompt_id) VALUES (?, ?, ?)", (user_id, location_id, prompt_id))
    connection.commit()
    connection.close()

def sync_approve_claim(user_id: int, location_id: str, prompt_id: str, proof_url: str, points: str):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM active_prompts WHERE user_id=? AND location_id=? AND prompt_id=?", (user_id, location_id, prompt_id))
    cursor.execute("INSERT INTO completed_prompts (user_id, location_id, prompt_id, proof_url, points) VALUES (?, ?, ?, ?, ?)", (user_id, location_id, prompt_id, proof_url, points))
    cursor.execute("UPDATE users SET points = COALESCE(points, 0) + ? WHERE user_id=?", (points, user_id))
    connection.commit()
    connection.close()
    
def sync_advance_user_level(user_id: int, new_idx: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET current_location_idx = ? WHERE user_id=?", (new_idx, user_id))
    connection.commit()
    connection.close()
    
def sync_save_pending_claim(message_id: int, user_id: int, location_id: str, prompt_id: str, proof_urls: list[str], points: str):
    joined_urls = "|||".join(proof_urls)
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO pending_claims (message_id, user_id, location_id, prompt_id, proof_urls, points) VALUES (?, ?, ?, ?, ?, ?)", (message_id, user_id, location_id, prompt_id, joined_urls, points))
    connection.commit()
    connection.close()
    
def sync_get_and_clear_pending_claim(message_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, location_id, prompt_id, proof_urls, points FROM pending_claims WHERE message_id=?", (message_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM pending_claims WHERE message_id=?", (message_id,))
        connection.commit()
        connection.close()
    return row

def sync_log_book(user_id: int, title: str, author: str, page_count: int, rating: int | None, points: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO books (user_id, title, author, page_count, rating, points) VALUES (?, ?, ?, ?, ?, ?)", (user_id, title, author, page_count, rating, points))
    cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    connection.commit()
    connection.close() 
    
def sync_get_user_books(user_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT title, author, page_count, rating, points, logged_at FROM books WHERE user_id=? ORDER BY id DESC", (user_id,))
    return cursor.fetchall()

def sync_get_books_autocomplete(user_id: int, current_query: str):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, author FROM books where user_id = ? AND title LIKE ? ORDER BY id DESC LIMIT 25", (user_id, f"%{current_query}%"))
    return cursor.fetchall()

def sync_delete_book(user_id: int, book_input: int):
    connection = get_db()
    cursor = connection.cursor()
    if book_input.digit():
        cursor.execute("SELECT id, title, points FROM books WHERE id=? AND user_id=?", (int(book_input), user_id),)
    else:
        cursor.execute("SELECT id, title, points FROM books WHERE title=? AND user_id=? ORDER BY id DESC LIMIT 1", (book_input, user_id),)
    row = cursor.fetchone()
    if not row: 
        return None
    book_id, title, points = row
    cursor.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, user_id),)
    cursor.execute("UPDATE users SET points = MAX(0, points-?) WHERE user_id = ?", (points, user_id),)
    connection.commit()
    connection.close()
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    new_total = cursor.fetchone()[0]
    return title, points, new_total
    

def sync_reset_user_stats(user_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET current_location_idx = 0, points = 0 WHERE user_id=?", (user_id,))
    cursor.execute("DELETE from active_prompts WHERE user_id=?", (user_id,))
    cursor.execute("DELETE from completed_prompts WHERE user_id=?", (user_id,))
    cursor.execute("DELETE from books WHERE user_id=?", (user_id,))
    connection.commit()
    connection.close()
    
def sync_set_guild_channel(guild_id: int, channel_type: str, channel_id: int):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO server_settings (guild_id) VALUES (?)", (guild_id,))
    cursor.execute(f"UPDATE server_settings SET {channel_type} = ? WHERE guild_id = ?", (channel_id, guild_id))
    connection.commit()
    connection.close()    
    
def sync_get_guild_settings(guild_id: int) -> tuple[int | None, int | None]:
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT submission_channel_id, response_channel_id FROM server_settings WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    return (row[0], row[1]) if row else (None, None)

def sync_get_leaderboard(metric: str):
    connection = get_db()
    cursor = connection.cursor()
    if metric == "points":
        cursor.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10")
        return cursor.fetchall(), "points"
    elif metric == "books":
        cursor.execute("SELECT user_id, COUNT(*) as ct FROM books GROUP by user_id ORDER BY ct DESC LIMIT 10")
        return cursor.fetchall(), "books"
    elif metric == "pages":
        cursor.execute("SELECT user_id, SUM(page_count) as total_pages FROM books GROUP BY user_id ORDER by total_pages DESC LIMIT 10")
        return cursor.fetchall(), "pages"   
    

# ============================================================
# Async Wrappers 
# ============================================================ 
async def get_user_stats(uid): return await asyncio.to_thread(sync_get_user_stats, uid)
async def get_profile_data(uid): return await asyncio.to_thread(sync_get_profile_data, uid)
async def get_prompt_statuses(uid, loc): return await asyncio.to_thread(sync_get_prompt_statuses, uid, loc)
async def add_active_prompts(uid, loc, pid): return await asyncio.to_thread(sync_add_active_prompt, uid, loc, pid)
async def approve_claim(uid, loc, pid, url, pts): return await asyncio.to_thread(sync_approve_claim, uid, loc, pid, url, pts)
async def advance_user_level(uid, idx): return await asyncio.to_thread(sync_advance_user_level, uid, idx)
async def save_pending_claim(mid, uid, loc, pid, url, pts): return await asyncio.to_thread(sync_save_pending_claim, mid, uid, loc, pid, url, pts)
async def get_and_clear_pending_claim(mid): return await asyncio.to_thread(sync_get_and_clear_pending_claim, mid)
async def log_book(uid, title, author, pgs, rating, pts): return await asyncio.to_thread(sync_log_book, uid, title, author, pgs, rating, pts)
async def get_user_books(uid): return await asyncio.to_thread(sync_get_user_books, uid)
async def get_books_autocomplete(uid, query): return await asyncio.to_thread(sync_get_books_autocomplete, uid, query)
async def delete_book(uid, bid): return await asyncio.to_thread(sync_delete_book, uid, bid)
async def reset_user_stats(uid): return await asyncio.to_thread(sync_reset_user_stats, uid)
async def set_guild_channel(gid, channel, cid): return await asyncio.to_thread(sync_set_guild_channel, gid, channel, cid)
async def get_guild_settings(gid): return await asyncio.to_thread(sync_get_guild_settings, gid)
async def reset_user_status(uid): return await asyncio.to_thread(sync_reset_user_stats, uid)
async def get_leaderboard(metric): return await asyncio.to_thread(sync_get_leaderboard, metric)


# ============================================================
# Buttons - for claim reviews
# ============================================================ 

class ClaimReview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, custom_id="approve_button")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await get_and_clear_pending_claim(interaction.message.id)
        if not data:
            await interaction.response.send_message("❌ This claim has already been resolved or cannot be found!", ephemeral=True)
            return
        
        user_id, loc_id, prompt_id, proof_urls_str, points = data
        location_data = LOCATION_MAP[loc_id]
        
        """
        message = interaction.message
        if not message.embeds:
            await interaction.response.send_message("❌ Cannot find submission embed!", ephemeral=True)
            return
            
        embed = message.embeds[0]
        desc = embed.description
        
        user_match = re.search(r"`(\d+)`", desc)
        loc_match = re.search(r"\*\*Location:\*\* (.+)", desc)
        prompt_match = re.search(r"\*\*Prompt:\*\* (.+)", desc)
        
        if not user_match or not loc_match or not prompt_match:
            await interaction.response.send_message("❌ Could not parse submission data!", ephemeral=True)
            return
        
        submit_id = int(user_match.group(1))
        loc_name = loc_match.group(1).strip()
        prompt_text = prompt_match.group(1).strip()
        
        location_data = next((l for l in LOCATIONS if l["name"].lower() == loc_name.lower()), None)
        if not location_data:
            await interaction.response.send_message("❌ Could not find location data!", ephemeral=True)
            return
        
        prompt_obj = next((p for p in location_data["prompts"] if p["text"] == prompt_text), None)
        if not prompt_obj:
            await interaction.response.send_message("❌ Could not find prompt data!", ephemeral=True)
            return

        proof_url = embed.image.url or (embed.fields[0].value if embed.fields else "")
        """
        
        await approve_claim(user_id, loc_id, prompt_id, proof_urls_str, points)
        
        current_idx, new_points = await get_user_stats(user_id)
        target_idx = LOCATION_ORDER.index(loc_id)
        _, completed = await get_prompt_statuses(user_id, loc_id)
        
        unlock_embed = None
        if len(completed) == len(location_data["prompts"]):
            if target_idx == current_idx and (target_idx + 1) < len(LOCATIONS):
                new_idx = current_idx + 1
                await advance_user_level(user_id, new_idx)
                current_location = LOCATIONS[current_idx]["name"]
                next_location = LOCATIONS[new_idx]["name"]
                next_story = LOCATIONS[new_idx]["story"]
                
                unlock_embed = discord.Embed(
                    title="📍New Location Unlocked",
                    description=(
                        f"You've completed {current_location} and unlocked {next_location}!!"
                    ),
                    color=discord.Color.teal(),
                )
                unlock_embed.add_field(
                    name="Next Level",
                    value=f"{next_story}"
                )
                unlock_embed.add_field(
                    name="Next Command",
                    value=f"Use '/{LOCATIONS[new_idx]['command']}' to draw your next challenge!"
                )
            elif target_idx == current_idx and (target_idx + 1) >= len(LOCATIONS):
                unlock_embed = discord.Embed(
                    title="Safehouse Reached",
                    description=(
                        f"Congratulations!! You've reached the safehouse!"
                    ),
                    color=discord.Color.gold(),
                )
        
        for child in self.children:
            child.disabled = True
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"Approved by {interaction.user.display_name}")
        await interaction.response.edit_message(embed=embed, view=self)
        
        _, response_channel_id = await get_guild_settings(interaction.guild_id)
        target_channel = interaction.guild.get_channel(response_channel_id) if response_channel_id else interaction.channel
        
        await target_channel.send(
            f"🎉 <@{user_id}> Your proof for **{prompt_id}** was **Approved**\n"
            f"You earned **+{points} points** (Total: `{new_points}` pts)."
        )
        
        if unlock_embed:
            await target_channel.send(
                content=f"<@{user_id}>", embed=unlock_embed
            )
            
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, custom_id="deny_button")
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await get_and_clear_pending_claim(interaction.message.id)
        if not data:
            await interaction.response.send_message("❌ This claim has already been resolved or cannot be found!", ephemeral=True)
            return
        
        """
        message = interaction.message
        embed = message.embeds[0]
        desc = embed.description
        
        user_match = re.search(r"`(\d+)`", desc)
        loc_match = re.search(r"\*\*Location:\*\* (.+)", desc)
        submitter_id = int(user_match.group(1)) if user_match else None
        loc_name = loc_match.group(1).strip() if loc_match else "Unknown Location"        
        """
        
        user_id, loc_id, prompt_id, _, _ = data
        location_data = LOCATION_MAP[loc_id]
        
        for child in self.children:
            child.disabled = True
        
        embed = interaction.message.embeds
        embed[0].color = discord.Color.dark_red()
        embed[0].set_footer(text=f"Denied by {interaction.user.display_name}")
        await interaction.response.edit_message(embed=embed, view=self)
        
        #channel = interaction.channel
        _, response_channel_id = await get_guild_settings(interaction.guild_id)
        target_channel = interaction.guild.get_channel(response_channel_id) if response_channel_id else interaction.channel
                
        
        await target_channel.send(
            f"❌ <@{user_id}> Your proof for **{prompt_id}** was **Denied**\n"
            f"Please resubmit with the correct proof\n" 
            f"If you would like clarification about why your claim was denied, please ping staff to ask!"
        )
        

# ============================================================
# Page View for Prompts
# ============================================================

class ViewLocationPrompts(discord.ui.View):
    def __init__(self, user_id: int, user_loc_index: int, initial_index: int = 0):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.user_loc_index = user_loc_index
        self.current_page = initial_index
        self.total_pages = len(LOCATIONS)
        self.update_buttons()
        
    def update_buttons(self):
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page >= self.total_pages - 1
        
    async def build_embed(self) -> discord.Embed:
        loc = LOCATIONS[self.current_page]
        active, completed = await get_prompt_statuses(self.user_id, loc["id"])
        is_unlocked = self.current_page <= self.user_loc_index
        
        embed = discord.Embed(
            title=f"Location {self.current_page + 1}: {loc['name']}",
            description=loc.get("description", loc['story']),
            color=discord.Color.dark_teal() if is_unlocked else discord.Color.dark_red(),
        )
        
        if not is_unlocked:
            embed.add_field(
                name="🔒 Location Locked",
                value="You must get through previous locations before unlocking these prompts!",
                inline=False,
            )
        else:
            for idx, p in enumerate(loc['prompts'], start=1):
                pid = p["id"]
                if pid in completed:
                    status=f"✅ **Completed** (+{p['points']} points)\n> {p['text']}"
                elif pid in active:
                    status=f"⏳ **In Progress** (+{p['points']} points)\n> {p['text']}"
                else:
                    status=f"⚠️ **Undiscovered** (+{p['points']} points)"
                    
                embed.add_field(
                    name=f"Prompt {idx} ({pid})",
                    value=status,
                    inline=False
                )
        
        embed.set_footer(text=f"Level {self.current_page + 1} of {self.total_pages} • Command: /{loc.get('command', 'draw')}")
        return embed
    
    @discord.ui.button(label="◀ Previous Location", style=discord.ButtonStyle.secondary, custom_id="prev_loc_btn")
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = await self.build_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next Location ▶", style=discord.ButtonStyle.secondary, custom_id="next_loc_btn")
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            embed = await self.build_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        

# ============================================================
# Book Log View 
# ============================================================

class BookLogView(discord.ui.View):
    def __init__(self, books: list, target_name: str, target_avatar_url: str, page_size: int = 5):
        super().__init__(timeout=120)
        self.books = books
        self.target_name = target_name
        self.target_avatar_url = target_avatar_url
        self.page_size = page_size
        self.current_page = 0
        self.total_pages = max(1, (len(books) + page_size - 1) // page_size)
        self.update_buttons()
        
    def update_buttons(self):
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page >= self.total_pages - 1
    
    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"📚 Survivor Book Log: {self.target_name}",
            description=f"Total Books Logged: **{len(self.books)}**",
            color=discord.Color.greyple(),
        )
        
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_books = self.books[start_idx:end_idx]
        
        for i, row in enumerate(page_books, start=start_idx + 1):
            title, author, pages, rating, pts, logged_at = row
            stars = f" | {'⭐' * rating}" if rating else ""
            date_str = logged_at.split()[0] if logged_at else "Unknown Date"
            
            embed.add_field(
                name=f"{i}. {title}",
                value=(
                    f"**Author:** {author}\n"
                    f"**Pages:** `{pages}`{stars}\n"
                    f"**Points Earned:** `+{pts}` points • Logged on {date_str}"
                ),
                inline=False,
            )
            
        embed.set_footer(text=f"Page {self.current_page + 1} of {self.total_pages}")
        return embed

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary, custom_id="prev_books_btn")
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = await self.build_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary, custom_id="next_book_btn")
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            embed = await self.build_embed()
            await interaction.response.edit_message(embed=embed, view=self)  
    

# ============================================================
# Leaderboard View 
# ============================================================

class LeaderboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        
    @discord.ui.select(
        placeholder="Choose Leaderboard Category",
        options=[
            discord.SelectOption(label="Most Points", value="points", emoji="⭐"),
            discord.SelectOption(label="Most Books Read", value="books", emoji="📚"),
            discord.SelectOption(label="Most Pages Read", value="pages", emoji="📄"),
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        metric = select.values[0]
        data, unit = await get_leaderboard(metric)
        title_map = {
            "points": "⭐ Most Points Leaderboard",
            "books": "📚 Most Books Read Leaderboard",
            "pages": "📄 Most Pages Read Leaderboard",
        }
        
        embed = discord.Embed(title=title_map[metric], color=discord.Color.gold())
        if not data:
            embed.description = "No Entries Yet!"
        else:
            lines = [f"**{i+1}**. <@{uid}> - `{score}` {unit}" for i, (uid, score) in enumerate(data)]
            embed.description = "\n".join(lines)
            
        await interaction.response.edit_message(embed=embed, view=self)
        



# ============================================================
# Bot Setup & Initialization
# ============================================================

intents = discord.Intents.default()

class PromptBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        setup_db()
        self.add_view(ClaimReview())
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} global slash commands.")

bot = PromptBot()

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="Listening to your screaming"
        )
    )
    print(f"Logged in as {bot.user} (Bot ID: {bot.user.id})")


"""
intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    setup_db()

    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    

    try:

        synced = await bot.tree.sync()

        #test_guild = discord.Object(id=1484666581274460330)
        #bot.tree.copy_global_to(guild=test_guild)
        #test_synced = await bot.tree.sync(guild=test_guild)
        
        print(
            f"Synced {len(synced)} global slash commands."
         )
        
        #print(
        #    f"Synced {len(test_synced)} test_server slash commands/"
        #)
        
    except Exception as error:
        print(
            f"Command sync error: {error}"
        )
"""    


# ============================================================
# Profile
# ============================================================

@bot.tree.command(name="profile", description="View your progress, current level, and stats")
async def profile_cmd(interaction: discord.Interaction, user: discord.Member | None = None):
    target = user or interaction.user
    loc_index, points, book_count, pages_read, prompts_done = await get_profile_data(target.id)
    total_prompts = sum(len(loc["prompts"]) for loc in LOCATIONS)
    
    current_loc_name = LOCATIONS[loc_index]["name"] if loc_index < len(LOCATIONS) else "Ultimate Survivor"
    
    embed = discord.Embed(title=f"🛡️ Survivor Profile: {target.display_name}", color=discord.Color.blurple())
    embed.add_field(name="Current Location", value=current_loc_name, inline=False)
    embed.add_field(name="Total Points", value=f"⭐ `{points}` points", inline=True)
    embed.add_field(name="Prompts Cleared", value=f"📜 `{prompts_done}` / `{total_prompts}`", inline=True)
    embed.add_field(name="Books Read", value=f"📚 `{book_count}`", inline=True)
    embed.add_field(name="Pages Read", value=f"📄 `{pages_read}`", inline=True)
    
    await interaction.response.send_message(embed=embed)
    



# ============================================================
# Draw Prompts
# ============================================================

async def handle_draw(interaction: discord.Interaction, target_loc_id: str):
    user_id = interaction.user.id
    current_idx, _ = await get_user_stats(user_id)
    target_idx = LOCATION_ORDER.index(target_loc_id)
    target_data = LOCATION_MAP[target_loc_id]
    
    if target_idx > current_idx:
        prev_name = LOCATIONS[target_idx - 1]["name"]
        await interaction.response.send_message(
            f"⛔ **{target_data['name']}** is locked! You must finish **{prev_name}** first!",
            ephemeral=True,
        )
        return
    
    active, completed = await get_prompt_statuses(user_id, target_loc_id)
    seen_ids = active.union(completed)
    available = [p for p in target_data["prompts"] if p["id"] not in seen_ids]
    
    if not available:
        if len(completed) == len(target_data["prompts"]):
            await interaction.response.send_message(f"✅You've completed all prompts in **{target_data['name']}!**", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️You've already drawn all prompts in **{target_data['name']}!** Submit your proof using /claim", ephemeral=True)
        return
    
    chosen = random.choice(available)
    await add_active_prompts(user_id, target_loc_id, chosen["id"])
    
    draw_embed = discord.Embed(
        title=f"**[{target_data['name']}] Prompt Drawn!**",
        description=f"📍{chosen['id']}: {chosen['text']}",
        color=discord.Color.dark_blue(),
        timestamp=datetime.datetime.now()
    )
    draw_embed.add_field(
        name="Points:",
        value=f"{chosen['points']} points"
    )
    
    await interaction.response.send_message(embed=draw_embed)
    
    
# ============================================================
# Draw Prompts - Slash Commands
# ============================================================
@bot.tree.command(name="cabin", description="Draw a prompt from The Abandoned Cabin")
async def cabin_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "abandoned-cabin") 

@bot.tree.command(name="town", description="Draw a prompt from Halloween Town")
async def town_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "halloween-town")

@bot.tree.command(name="tower", description="Draw a prompt from The Tower of Terror")
async def tower_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "tower-of-terror")  
    
@bot.tree.command(name="trail", description="Draw a prompt from The Trick or Treat Trail")
async def trail_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "trick-or-treat-trail")

@bot.tree.command(name="hideout", description="Draw a prompt from The Final Girl Hideout")
async def hideout_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "final-girl-hideout") 
    
@bot.tree.command(name="cemetery", description="Draw a prompt from The Haunted Cemetery")
async def cemetery_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "haunted-cemetery")

@bot.tree.command(name="lair", description="Draw a prompt from The Creature's Lair")
async def lair_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "creature's-lair") 

@bot.tree.command(name="festival", description="Draw a prompt from The Festival Grounds")
async def festival_cmd(interaction: discord.Interaction):
    await handle_draw(interaction, "festival-grounds")   


# ============================================================
# View Prompts Command
# ============================================================

@bot.tree.command(name="view_prompts", description="View prompts by location and check your progress",)
async def view_prompts_cmd(interaction: discord.Interaction):
    user_id = interaction.user.id
    current_index, _ = await get_user_stats(user_id)
    
    start_page = min(current_index, len(LOCATIONS) - 1)
    
    view = ViewLocationPrompts(
        user_id=user_id,
        user_loc_index=current_index,
        initial_index=start_page
    )
    
    embed = await view.build_embed()
    await interaction.response.send_message(embed=embed, view=view)


# ============================================================
# Claim Command
# ============================================================

async def prompt_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    selected_location = interaction.namespace.location
    if not selected_location:
        return []
    
    active, _ = await get_prompt_statuses(interaction.user.id, selected_location)
    location_data = LOCATION_MAP.get(selected_location)
    if not location_data:
        return []
    
    choices = []
    for p in location_data["prompts"]:
        if p["id"] in active:
            label = f"[{p['points']} pts] {p['id']}: {p['text']}"[:100]
            if current.lower() in label.lower():
                choices.append(app_commands.Choice(name=label, value=p["id"]))
                
    return choices[:25]


@bot.tree.command(name="claim", description="Submit proof for a prompt you've drawn!")
@app_commands.describe(
    location="The location of the prompt",
    prompt="Select from your drawn prompts for your current location",
    proof_1="Primary proof of completion (required)",
    proof_2="Second proof image (optional)",
    proof_3="Third proof image (optional)",
    proof_4="Fourth proof image (optional)"
)
@app_commands.choices(
    location=[app_commands.Choice(name=loc["name"], value=loc["id"]) for loc in LOCATIONS]
)
@app_commands.autocomplete(prompt=prompt_autocomplete)
async def claim_command(
    interaction: discord.Interaction,
    location: str,
    prompt: str,
    proof_1: discord.Attachment,
    proof_2: discord.Attachment | None = None,
    proof_3: discord.Attachment | None = None,
    proof_4: discord.Attachment | None = None,
    
):
    if not interaction.guild_id:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    
    submission_channel_id, response_channel_id = await get_guild_settings(interaction.guild_id)
    if not submission_channel_id or not response_channel_id:
        await interaction.response.send_message("⚠️ The server administrators have not set up the submission and response channels yet.", ephemeral=True)
        return
    
    submission_channel = interaction.guild.get_channel(submission_channel_id)
    if not submission_channel:
        await interaction.response.send_message("❌ The configured submission channel was deleted or couldn't be found.", ephemeral=True)
    
    user_id = interaction.user.id
    active, _ = await get_prompt_statuses(user_id, location)
    
    if prompt not in active:
        await interaction.response.send_message("❌ This prompt is not available for you right now.", ephemeral=True)
        return
    
    location_data = LOCATION_MAP[location]
    prompt_obj = next((p for p in location_data["prompts"] if p["id"] == prompt), None)
    if not prompt_obj:
        await interaction.response.send_message("❌ Prompt data not found.", ephemeral=True)
        return
    
    attachments = [p for p in [proof_1, proof_2, proof_3, proof_4] if p is not None]
    proof_urls = [a.url for a in attachments]
    gallery_url = "https://discord.com"

    embed = discord.Embed(
        title="📥 New Prompt Submission",
        url=gallery_url,
        description=f"**User:** {interaction.user.mention} ({'interaction.user.id'})\n"
                    f"**Location:** {location_data['name']}\n"
                    f"**Prompt ID:** {prompt_obj['id']}\n"
                    f"**Prompt:** {prompt_obj['text']}\n"
                    f"**Reward:** {prompt_obj['points']} points",
        color = discord.Color.gold(),
    )
    
    embed.set_image(url=attachments[0].url)
    embeds_to_send = [embed]
    
    for a in attachments[1:]:
        extra_embed = discord.Embed(url=gallery_url)
        extra_embed.set_image(url=a.url)
        embeds_to_send.append(extra_embed)
    
    """
    if proof.content_type and proof.content_type.startswith("image/"):
        embed.set_image(url=proof.url)
    else:
        embed.add_field(name="Proof File", value=f"[{proof.filename}]({proof.url})", inline=False)
    """
        
    review_msg = await submission_channel.send(embed=embeds_to_send, view = ClaimReview())
    await asyncio.to_thread(sync_save_pending_claim, review_msg.id, user_id, location, prompt, proof_urls, prompt_obj["points"])
    
    await interaction.response.send_message(
        "✅ Your claim was submitted for review! You will be pinged once approved or denied!",
        ephemeral=True
    )
    

# ============================================================
# Log Books
# ============================================================

@bot.tree.command(name="log_book", description="Log finished books to earn points!")
@app_commands.describe(
    title="Title of the book",
    author="Author of the book",
    pages="Total page count",
    rating="Optional rating of the book (out of 5 stars)"
)
@app_commands.choices(rating=[
    app_commands.Choice(name="⭐ 1 Star", value=1),
    app_commands.Choice(name="⭐⭐ 2 Stars", value=2),
    app_commands.Choice(name="⭐⭐⭐ 3 Stars", value=3),
    app_commands.Choice(name="⭐⭐⭐⭐ 4 Stars", value=4),
    app_commands.Choice(name="⭐⭐⭐⭐⭐ 5 Stars", value=5),  
])
async def log_book_cmd(
  interaction: discord.Interaction,
  title: str,
  author: str,
  pages: int,
  rating: int| None = None  
):
    if pages <= 0:
        await interaction.response.send_message("❌ Page count must be greater than 0.", ephemeral=True)
        return
    
    awarded_points = max(5, pages // 10)
    
    await log_book(interaction.user.id, title, author, pages, rating, awarded_points)
    _, total_points = await get_user_stats(interaction.user.id)
    
    stars = f"| Rating: {'⭐' * rating}" if rating else ""
    embed = discord.Embed(
        title="📖 Book Logged!",
        description=f"**{title}** by *{author}*\nPages: `{pages}`{stars}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Points Earned", value=f"{awarded_points} points", inline=True)
    embed.add_field(name="Total Points", value=f"{total_points} points", inline=True)
    await interaction.response.send_message(embed=embed)
    

# ============================================================
# Delete Books
# ============================================================

async def user_books_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    rows = await get_books_autocomplete(interaction.user.id, current)
    choices = []
    for book_id, title, author in rows:
        display_label = f"{title} by {author}"
        if len(display_label) > 100:
            display_label = display_label[:97] + "..."
        choices.append(app_commands.Choice(name=display_label, value=str(book_id)))
    return choices

@bot.tree.command(name="delete_book", description="Delete an entry from your reading log and deduct its points")
@app_commands.describe(book="Select one of your logged books to delete")
@app_commands.autocomplete(book=user_books_autocomplete)
async def delete_books_cmd(interaction: discord.Interaction, book: str):
    result = delete_book(interaction.user.id, book)
    if not result:
        await interaction.response.send_message("❌ This book was not found in your log", ephemeral=True)
        return
    
    title, points_lost, new_points = result
    
    embed = discord.Embed(
        title="🔖 Book Log Deleted",
        description=f"**{title}** has been removed from your book log",
        color=discord.color.blue()
    )
    embed.add_field(name="Points Deducted", value=f"-{points_lost} points", inline=True)
    embed.add_field(name="Updated Points", value=f"{new_points} points", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    

# ============================================================
# View Books
# ============================================================

@bot.tree.command(name="view_books", description="View a list of all the books you have logged")
async def view_books_cmd(interaction: discord.Interaction):
    target = interaction.user
    books = await get_user_books(target.id)
    
    if not books:
        await interaction.response.send_message("📖 You haven't logged any books yet! Use '/log_book' to log your first book!", ephemeral=True)
        return
    
    view = BookLogView(
        books=books,
        target_name=target.display_name,
        target_avatar_url=target.display_avatar.url,
    )
    
    if view.total_pages == 1:
        await interaction.response.send_message(embed=view.build_embed())
    else:
        await interaction.response.send_message(embed=view.build_embed(), view=view)
        

# ============================================================
# Leaderboard
# ============================================================

@bot.tree.command(name="leaderboard", description="View the rankings for most points, most books, and most pages")
async def leaderboard_cmd(interaction: discord.Interaction):
    data, unit = await get_leaderboard("points")
    embed = discord.Embed(title="⭐ Most Points Leaderboard", color=discord.Color.gold())
    lines = [f"**{i+1}**. <@{uid}>  - `{score}` {unit}" for i, (uid, score) in enumerate(data)] if data else ["No entries yet!"]
    embed.description = "\n".join(lines)
    
    await interaction.response.send_message(embed=embed, view=LeaderboardView())

    
    


# ============================================================
# Admin: Set Submission Channel
# ============================================================

@bot.tree.command(
    name="set_submission_channel",
    description="Admin: set the submission channel for claims"
)
@app_commands.describe(channel="The channel for staff to review pending claims")
@app_commands.checks.has_permissions(administrator=True)
async def set_submission_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await set_guild_channel(interaction.guild_id, "submission_channel_id", channel.id)
    await interaction.response.send_message(f"Successfully set the submission channel to {channel.mention}!", ephemeral = True)
@set_submission_channel.error
async def set_submission_channel_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)


# ============================================================
# Admin: Set Submission Response Channel
# ============================================================

@bot.tree.command(
    name="set_response_channel",
    description="Admin: set the channel to respond to approval/denial submisisons"
)
@app_commands.describe(channel="The channel where users will be pinged with claim results")
@app_commands.checks.has_permissions(administrator=True)
async def set_response_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await set_guild_channel(interaction.guild_id, "response_channel_id", channel.id)
    await interaction.response.send_message(f"Successfully set the submission response channel to {channel.mention}!", ephemeral = True)
@set_response_channel.error
async def set_response_channel_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)
        

# ============================================================
# Admin: Reset User Stats
# ============================================================
@bot.tree.command(
    name="admin_reset_user",
    description="Admin: completely resets a user's points, locations, and prompts"
)
@app_commands.describe(user="The user whose progress you want to reset")
@app_commands.checks.has_permissions(administrator=True)
async def admin_reset_user(interaction: discord.Interaction, user: discord.Member):
    await reset_user_stats(user.id)
    await interaction.response.send_message(f"Successfully reset all progress and points for {user.mention}!", ephemeral=True)
@admin_reset_user.error
async def admin_reset_user_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)




# ============================================================
# Start Running Bot
# ============================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN environment variable is missing."
    )

setup_db()

bot.run(TOKEN)