package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
)

const HelloMessage = "Привет! Отправь фото или видео, чтобы я его обработал"

type RawMessage struct {
	Message string
	ChatId  int64
	ReplyTo int
}

type PhotoFaceResp struct {
	Traits      map[string][]string `json:"traits"`
	Probability float32             `json:"probability"`
}

func MessagePrinter(bot *tgbotapi.BotAPI, ch <-chan RawMessage) {
	for st := range ch {
		msg := tgbotapi.NewMessage(st.ChatId, st.Message)
		msg.ReplyToMessageID = st.ReplyTo
		msg.ParseMode = tgbotapi.ModeMarkdown
		bot.Send(msg)
	}
}

func CreateMessages(el [][]PhotoFaceResp) []string {
	out := make([]string, 0, len(el))

	for _, face := range el {
		builder := strings.Builder{}
		met := make(map[string]bool) // Судя по всему, иногда, когда мало вариантов, постгрес возвращает дубли

		for _, match := range face {
			if !met[match.Traits["name"][0]] {
				builder.WriteString(fmt.Sprintf("**%s**\nVK: %s\nProbability: %f\n\n", match.Traits["name"][0], match.Traits["vk_url"][0], 1-match.Probability))
			}

			met[match.Traits["name"][0]] = true
		}

		out = append(out, builder.String())
	}

	return out
}

func ProcessPhotos(bot *tgbotapi.BotAPI, message *tgbotapi.Message, toPrinter chan<- RawMessage) {
	photo := make([]byte, 0)

	str, _ := bot.GetFileDirectURL((*message.Photo)[len(*message.Photo)-1].FileID)

	resp, err := http.Get(str)

	if err != nil {
		panic(err)
	}

	defer resp.Body.Close()

	photo, _ = ioutil.ReadAll(resp.Body)

	se, _ := json.Marshal(map[string]interface{}{
		"face": Encode(photo),
	})

	resp, err = http.Post("http://ff_corecomp:3800/api/core/recface", "application/json", bytes.NewBuffer(se))
	if err != nil {
		panic(err)
	}

	body, _ := ioutil.ReadAll(resp.Body)

	if resp.StatusCode != 200 {
		return
	}

	defer resp.Body.Close()

	coreResp := make([][]PhotoFaceResp, 0, 0) // Для каждого фото, для каждого человека, несколько метчей

	err = json.Unmarshal(body, &coreResp)

	if err != nil {
		panic(err)
	}

	for _, msg := range CreateMessages(coreResp) {
		toPrinter <- RawMessage{Message: msg, ChatId: message.Chat.ID, ReplyTo: message.MessageID}
	}
}

func ProcessVideos(bot *tgbotapi.BotAPI, message *tgbotapi.Message, toPrinter chan<- RawMessage) {
	photo := make([]byte, 0)

	str, err := bot.GetFileDirectURL(message.Video.FileID)

	if err != nil {
		panic(err)
	}

	resp, err := http.Get(str)

	if err != nil {
		panic(err)
	}

	defer resp.Body.Close()

	photo, _ = ioutil.ReadAll(resp.Body)

	se, _ := json.Marshal(map[string]interface{}{
		"video": Encode(photo),
	})

	resp, err = http.Post("http://ff_videocomp:3800/api/video", "application/json", bytes.NewBuffer(se))
	if err != nil {
		panic(err)
	}

	body, _ := ioutil.ReadAll(resp.Body)

	if resp.StatusCode != 200 {
		return
	}

	defer resp.Body.Close()

	coreResp := make([][]PhotoFaceResp, 0, 0)

	err = json.Unmarshal(body, &coreResp)

	if err != nil {
		panic(err)
	}

	for _, msg := range CreateMessages(coreResp) {
		toPrinter <- RawMessage{Message: msg, ChatId: message.Chat.ID, ReplyTo: message.MessageID}
	}
}
