import requests
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

API_KEY = 'YOUR_TELEGRAM_BOT_API_KEY'
bot = telebot.TeleBot(API_KEY)

url = "https://movie-database-imdb-alternative.p.rapidapi.com/"

headers = {
    'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com",
    'x-rapidapi-key': "YOUR_API_KEY"
    }

global bot_msg_id

@bot.message_handler(commands=['help'])
def help(message):
    msg="I can provide you with information about movies, tv shows and web series.\n\nUse */info* command followed by name of a Movie/TV Show/Web-Series.\n\nEg: `/info Interstellar`\n(Tap to Copy)"
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def media_selection(message):
  request=message.text.split()
  if len(request) < 2 or request[0].lower() not in "/info":
    bot.send_message(message.chat.id, "Pass the name of the Movie/TV Show/Web-Series you want Info about.\n\nEg: `/info Interstellar`\n(Tap To Copy)", parse_mode='Markdown')
  else:
    title= ' '.join(message.text.split()[1:])
    querystring = {"s":title,"page":"1"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    response_data=response.json()
    if response_data["Response"]=="False":
        bot.send_message(message.chat.id, "No Data Found😢")
    else:
        total_results = response_data["totalResults"]
        if int(total_results) > 1 :
            reply_medias_keyboard=ReplyKeyboardMarkup(input_field_placeholder="Select Media")
            for media in response_data["Search"]:
                reply_medias_keyboard.add(KeyboardButton(media["imdbID"]+" "+media["Title"]))

            global bot_msg_id
            bot_msg_id=bot.send_message(message.chat.id, "Select Media", reply_markup=reply_medias_keyboard).message_id
        else:
            media_info(response_data["Search"][0]["imdbID"], message.chat.id)

def media_info(media_id, message_chat_id):
    msg_id=bot.send_message(message_chat_id, "*Getting Info*", parse_mode='Markdown').message_id

    querystring = {"i":media_id, "plot":"short"}
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        media_data=response.json()

        if media_data["Response"]=="False":
            bot.send_message(message_chat_id, "Incorrect ❌ ID")
        else:
            media_poster=media_data["Poster"]
            media_title=media_data["Title"]
            media_years=media_data["Year"]
            media_rated=media_data["Rated"]
            media_released=media_data["Released"]
            media_runtime=media_data["Runtime"]
            media_genre=media_data["Genre"]
            media_director=media_data["Director"]
            media_actors=media_data["Actors"]
            media_plot=media_data["Plot"]
            media_imbd_rating=media_data["imdbRating"]
            media_language=media_data["Language"]
            media_awards=media_data["Awards"]

            message_caption="*Title: *"+media_title+"\n\n*Released On: *"+media_released+"\n\n*Year(s): *"+media_years+"\n\n*Content Rating: *"+media_rated+"\n\n*Runtime: *"+media_runtime

            if media_data["Type"]=="movie":
                media_box_office=media_data["BoxOffice"]
                message_caption+="\n\n*Box Office: *"+media_box_office
            else:
                media_total_seasons=media_data["totalSeasons"]
                message_caption+="\n\n*Total Seasons: *"+media_total_seasons

            message_caption+="\n\n*Genre: *"+media_genre+"\n\n*IMDb Ratings: *"+media_imbd_rating+"⭐"+"\n\n*Language(s): *"+media_language+"\n\n*Director(s): *"+media_director+"\n\n*Actors: *"+media_actors+"\n\n*Awards: *"+media_awards+"\n\n*Plot: *"+media_plot

            bot.delete_message(message_chat_id, msg_id)
            bot.send_photo(message_chat_id, media_poster, message_caption, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    except:
        bot.send_message(message_chat_id, "An Error Occured. Try Again Later")

def check_id(message):
    media_id=message.text.split()[0]
    if media_id.startswith("tt"):
        return True
    else:
        bot.send_message(message.chat.id, "Incorrect Input\n\nUse */help* command to understand how this bot works", reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
        return False

@bot.message_handler(func=check_id)
def reply_keyboard_handler(message):
    media_id=message.text.split()[0]
    bot.delete_message(message.chat.id, bot_msg_id)
    bot.delete_message(message.chat.id, message.message_id)
    media_info(media_id,message.chat.id)

bot.polling(non_stop=True)

