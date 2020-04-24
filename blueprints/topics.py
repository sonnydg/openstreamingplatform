from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_security import current_user

from classes.shared import db
from classes import settings
from classes import topics
from classes import Stream
from classes import RecordedVideo

from functions import themes

topics_bp = Blueprint('topic', __name__, url_prefix='/topic')

@topics_bp.route('/')
def topic_page():
    sysSettings = settings.settings.query.first()
    if sysSettings.showEmptyTables:
        topicsList = topics.topics.query.all()
    else:
        topicIDList = []
        for streamInstance in db.session.query(Stream.Stream.topic).distinct():
            topicIDList.append(streamInstance.topic)
        for recordedVidInstance in db.session.query(RecordedVideo.RecordedVideo.topic).distinct():
            if recordedVidInstance.topic not in topicIDList:
                topicIDList.append(recordedVidInstance.topic)

        topicsList = []

        for item in topicIDList:
            topicQuery = topics.topics.query.filter_by(id=item).first()
            if topicQuery is not None:
                topicsList.append(topicQuery)

    topicsList.sort(key=lambda x: x.name)

    return render_template(themes.checkOverride('topics.html'), topicsList=topicsList)


@topics_bp.route('/<topicID>/')
def topic_view_page(topicID):
    topicID = int(topicID)
    streamsQuery = Stream.Stream.query.filter_by(topic=topicID).all()
    recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(topic=topicID, pending=False, published=True).all()

    # Sort Video to Show Newest First
    recordedVideoQuery.sort(key=lambda x: x.videoDate, reverse=True)

    clipsList = []
    for vid in recordedVideoQuery:
        for clip in vid.clips:
            if clip.published is True:
                clipsList.append(clip)

    clipsList.sort(key=lambda x: x.views, reverse=True)

    return render_template(themes.checkOverride('videoListView.html'), openStreams=streamsQuery, recordedVids=recordedVideoQuery, clipsList=clipsList, title="Topics - Videos")
