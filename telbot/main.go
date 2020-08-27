package main

import (
	"log"
	"os"

	"github.com/go-telegram-bot-api/telegram-bot-api"
)

func main() {

	token := os.Getenv("TOKEN")
	bot, err := tgbotapi.NewBotAPI(token)

	if err != nil {
		log.Panic(err)
	}

	toPrinter := make(chan RawMessage, 16)

	go MessagePrinter(bot, toPrinter)

	log.Printf("Authorized on account %s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	updates, err := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message == nil {
			continue
		}

		if update.Message.IsCommand() && update.Message.Text == "/start" {
			msg := tgbotapi.NewMessage(update.Message.Chat.ID, HelloMessage)
			bot.Send(msg)
			continue
		}

		if update.Message.Photo != nil {
			go ProcessPhotos(bot, update.Message, toPrinter)
		}

		// TODO: VideoComp integration
	}
}
