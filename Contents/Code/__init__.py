from updater import Updater

TITLE = 'Title'
PREFIX = '/video/adultswim'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
BASE_URL = 'https://www.adultswim.com'
API = '%s/api' % (BASE_URL)
VIDEO_API = '%s/videos/api/v3/media' % (BASE_URL)


def Start():
    ObjectContainer.title1 = L(TITLE)
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    TVShowObject.thumb = R(ICON)
    TVShowObject.art = R(ART)

    SeasonObject.thumb = R(ICON)
    SeasonObject.art = R(ART)

    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)

    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

@handler(PREFIX, L(TITLE), thumb = ICON, art = ART)

def MainMenu():
    # oc = ObjectContainer(
    #     objects = [
    #         DirectoryObject(
    #             key = Callback(ShowsMenu),
    #             title = L('Shows')
    #         ),
    #         DirectoryObject(
    #             key = Callback(LiveStreamsMenu),
    #             title = L('Live Streams')
    #         )
    #     ]
    # )
    # Updater('%s/update' %(PREFIX), oc)
    # return oc
    return ShowsMenu()

@route('%s/shows' % (PREFIX))
def ShowsMenu():
    oc = ObjectContainer(
        content = ContainerContent.Shows,
        title1 = L('Shows')
    )

    shows = JSON.ObjectFromURL('%s/shows/v1/collections' % (API))
    for show in shows['data']['collections']:
        oc.add(
            TVShowObject(
                key = Callback(SeasonsMenu, show = show['title'], slug = show['slug']),
                rating_key = show['id'],
                #genres = ,
                #tags = ,
                #duration = ,
                #rating = ,
                #source_title = ,
                title = show['title'],
                #summary = ,
                #originally_available_at = ,
                #content_rating = ,
                #studio = ,
                #countries = ,
                thumb = show['poster'],
                #art = ,
                #episode_count = ,
            )
        )
    return oc

@route('%s/seasons' % (PREFIX), show = str, slug = str)
def SeasonsMenu(show, slug, **kwargs):
    oc = ObjectContainer(
        content = ContainerContent.Seasons,
        title1 = show
    )

    collections = JSON.ObjectFromURL('%s/shows/v1/collections/by-slug/%s/videos?order_videos=true&include_page=true&fields=description,title_id,season_number,tv_rating,type,title,collection_id,duration,episode_number,collection_title,poster,slug,launch_date,clip_order' % (API, slug))

    thumb = collections['data']['page']['meta_thumbnail']
    art = collections['data']['page']['background_image']

    seasons = collections['data']['videos']
    for season in seasons:
        oc.add(
            SeasonObject(
                key = Callback(EpisodesMenu, slug = slug, season = season, videos = season['videos'], art = art),
                #summary = ,
                rating_key = '%s-s%i' % (slug, int(season['number'])),
                index = int(season['number']),
                title = season['name'],
                show = show,
                episode_count = len(season['videos']),
                #source_title = ,
                thumb = thumb,
                art = art,
            )
        )
    return oc

@route('%s/episodes' % (PREFIX), slug = str, season = list, videos = list, art = str)
def EpisodesMenu(slug, season, videos, art, **kwargs):
    oc = ObjectContainer(
        content = ContainerContent.Episodes,
        title1 = season['name']
    )

    for video in videos:
        oc.add(
            EpisodeObject(
                key = Callback(Lookup, slug = slug, season = season, video = video, art = art),
                rating_key = '%s-s%ie%i' % (slug, int(video['season_number']), int(video['episode_number'])),
                title = video['title'],
                summary = video['description'],
                #originally_available_at = ,
                #rating = ,
                #writers = ,
                #directors = ,
                #producers = ,
                #guest_stars = ,
                #absolute_index = ,
                show = video['collection_title'],
                season = int(video['season_number']),
                thumb = video['poster'],
                art = art,
                #source_title = ,
                duration = int(float(video['duration']) * 1000),
                items = [
                    MediaObject(
                        parts = [
                            PartObject(
                                key = HTTPLiveStreamURL(Callback(PlayVideo, videoID = video['id']))
                            )
                        ]
                    )
                ]
            )
        )
    return oc

@route('%s/lookup' % (PREFIX), slug = str, video = list, art = str)
def Lookup(slug, video, art, **kwargs):
    oc = ObjectContainer()

    oc.add(
        EpisodeObject(
            key = Callback(Lookup, slug = slug, video = video, art = art),
            rating_key = '%s-s%ie%i' % (slug, int(video['season_number']), int(video['episode_number'])),
            title = video['title'],
            summary = video['description'],
            #originally_available_at = ,
            #rating = ,
            #writers = ,
            #directors = ,
            #producers = ,
            #guest_stars = ,
            #absolute_index = ,
            show = video['collection_title'],
            season = int(video['season_number']),
            thumb = video['poster'],
            art = art,
            #source_title = ,
            duration = int(float(video['duration']) * 1000),
            items = [
                MediaObject(
                    parts = [
                        PartObject(
                            key = HTTPLiveStreamURL(Callback(PlayVideo, videoID = video['id']))
                        )
                    ]
                )
            ]
        )
    )
    return oc

@route('%s/play' % (PREFIX), videoID = str)
def PlayVideo(videoID, **kwargs):
    media = JSON.ObjectFromURL('%s/%s' % (VIDEO_API, videoID))
    return Redirect(media['media']['tv']['unprotected']['url'])