from flask import Flask, render_template, request, redirect, url_for
from bson import ObjectId
from pymongo import MongoClient
from decouple import config

application = Flask(__name__)
title = "YouTube Videos Manager"
heading = "Videos Manager"

client = MongoClient(config('MONGO_URL'))

db = client.videos

videos = db.flaskVideos


def redirect_url():
	return request.args.get('next') or request.referrer or url_for('index')


@application.route("/")
def lists():
	videos_l = videos.find()
	return render_template(
		'index.html', videos=videos_l, t=title, h=heading
	)


@application.route("/action", methods=['POST'])
def action():
	name = request.values.get("name")
	theme = request.values.get("theme")
	likes = 0
	unlikes = 0
	videos.insert(
		{"name": name, "theme": theme, 'likes': likes, 'unlikes': unlikes}
	)
	return redirect("/")


@application.route("/add_like", methods=['GET'])
def add_like():
	id = request.values.get("_id")
	video = videos.find_one({"_id": ObjectId(id)})
	likes = video['likes'] + 1
	name = video['name']
	theme = video['theme']
	unlikes = video['unlikes']
	videos.update(
		{"_id": ObjectId(id)},
		{"name": name, "theme": theme, 'likes': likes, 'unlikes': unlikes}
	)
	return redirect("/")


@application.route("/add_unlike", methods=['GET'])
def add_unlike():
	id = request.values.get("_id")
	video = videos.find_one({"_id": ObjectId(id)})
	unlikes = video['unlikes'] + 1
	likes = video['likes']
	name = video['name']
	theme = video['theme']
	videos.update(
		{"_id": ObjectId(id)},
		{"name": name, "theme": theme, 'likes': likes, 'unlikes': unlikes}
	)
	return redirect("/")


@application.route("/list_themes", methods=['GET'])
def list_themes():
	videos_l = videos.find()
	videos_list = list(videos_l)
	themes = []
	for data in videos_list:
		for item in data['theme']:
			if data['theme'] not in themes:
				themes.append(data['theme'])
	list_themes = []
	
	for item in themes:
		themes_dict = {}
		classification = 0
		for data in videos_list:
			if item == data['theme']:
				classification += data['likes'] - (data['unlikes'] / 2)
	
		themes_dict['theme'] = item
		themes_dict['classification'] = int(classification)
		if themes_dict not in list_themes:
			list_themes.append(themes_dict)
	list_themes_sorted = sorted(
		list_themes, key=lambda k: k['classification'], reverse=True
	)
	return render_template(
		'list_themes.html', videos=list_themes_sorted, t=title, h=heading
	)


wsgi_app = application.wsgi_app

if __name__ == "__main__":
	application.run("0.0.0.0")
