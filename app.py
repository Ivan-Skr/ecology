from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Place, Comment, Event
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///main.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/sbor', methods=['POST', 'GET'])
def sbor():
    if request.method == 'POST':
        search = request.form.get('search')
        yandex_results = requests.get(f'https://search-maps.yandex.ru/v1/?text=город {search}, пункт сбора&type=biz&lang=ru_RU&apikey=07bb2b4c-c44c-4112-9ef1-dd1d3c839e34').json()['features']
        yandex_list = [_['properties']['description'] for _ in yandex_results]

        local_results = session.query(Place).filter(Place.name.ilike(f'%{search}%')).all()
        local_list = [place.description for place in local_results]

        combined_list = yandex_list + local_list
        return render_template('punkti_sbora.html', listt=combined_list)
    else:
        default_list = ['Ногинск: ТК Богородский, ул. 3-го Интернационала, д. 62',
                        'Орехово-Зуево: ТЦ Орех, ул. Ленина, д. 78',
                        'Воскресенск: Парк Москворецкий',
                        'Коломна: Сквер Центральный, Площадь Советская, д. 6',
                        'Чехов: ТЦ Радуга, ул. Советская, д. 80А']
        return render_template('punkti_sbora.html', listt=default_list)

@app.route('/park', methods=['POST', 'GET'])
def park():
    if request.method == 'POST':
        search = request.form.get('search')
        yandex_results = requests.get(f'https://search-maps.yandex.ru/v1/?text=город {search}, парк&type=biz&lang=ru_RU&apikey=07bb2b4c-c44c-4112-9ef1-dd1d3c839e34').json()['features']
        yandex_list = [_['properties']['description'] for _ in yandex_results]

        local_results = session.query(Place).filter(Place.name.ilike(f'%{search}%')).all()
        local_list = [place.description for place in local_results]

        combined_list = yandex_list + local_list
        return render_template('park.html', listt=combined_list)
    else:
        default_list = ['Московская область, Электросталь, парк Авангард',
                        'Московская область, Электросталь, Восточный парк',
                        'Московская область, Электросталь, сквер имени С.И. Золотухи',
                        'Московская область, Богородский городской округ, Ногинск, Истомкинская роща',
                        'Московская область, Богородский городской округ, Ногинск, сквер Карла Маркса']
        return render_template('park.html', listt=default_list)


@app.route('/show_park/<adress>', methods=['POST', 'GET'])
def show_park(adress):
    res = requests.get(f'https://search-maps.yandex.ru/v1/?text={adress}&type=biz&lang=ru_RU&apikey=07bb2b4c-c44c-4112-9ef1-dd1d3c839e34').json()['features'][0]
    if 'Phones' in res['properties']['CompanyMetaData'].keys():
        phones = [_['formatted'] for _ in res['properties']['CompanyMetaData']['Phones']]
    else:
        phones = ''

    if 'Hours' in res['properties']['CompanyMetaData'].keys():
        hours = res['properties']['CompanyMetaData']['Hours']['text']
    else:
        hours = ''
    data = {
        'description': res['properties']['description'],
        'phones': phones,
        'hours': hours
    }
    coords = res['geometry']['coordinates']
    pic = requests.get(f'https://static-maps.yandex.ru/v1?ll={coords[0]},{coords[1]}&lang=ru_RU&size=450,450&z=17&pt=37.620070,55.753630,pmwtm1~37.64,55.76363,pmwtm99&apikey=85950243-e5f2-488a-8ecc-1cd21cd181e2')
    with open("static/img/img.jpg", "wb") as out:
        out.write(pic.content)

    place = session.query(Place).filter_by(name=adress).first()
    if not place:
        place = Place(name=adress)
        session.add(place)
        session.commit()

    if request.method == 'POST':
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        if comment:
            new_comment = Comment(text=comment, place_id=place.id)
            session.add(new_comment)
            session.commit()
        if rating:
            rating = int(rating)
            place.num_ratings += 1
            place.rating = ((place.rating * (place.num_ratings - 1)) + rating) / place.num_ratings
            session.commit()

    comments = session.query(Comment).filter_by(place_id=place.id).all()
    return render_template('show_park.html', data=data, comments=comments, rating=place.rating, num_ratings=place.num_ratings)


@app.route('/show_sbor/<adress>', methods=['POST', 'GET'])
def show_sbor(adress):
    res = requests.get(f'https://search-maps.yandex.ru/v1/?text={adress}&type=biz&lang=ru_RU&apikey=07bb2b4c-c44c-4112-9ef1-dd1d3c839e34').json()['features'][0]

    if 'Phones' in res['properties']['CompanyMetaData'].keys():
        phones = [_['formatted'] for _ in res['properties']['CompanyMetaData']['Phones']]
    else:
        phones = ''

    if 'Hours' in res['properties']['CompanyMetaData'].keys():
        hours = res['properties']['CompanyMetaData']['Hours']['text']
    else:
        hours = ''
    
    data = {
        'description': res['properties']['description'],
        'phones': phones,
        'hours': hours
    }
    
    coords = res['geometry']['coordinates']
    pic = requests.get(f'https://static-maps.yandex.ru/v1?ll={coords[0]},{coords[1]}&lang=ru_RU&size=450,450&z=17&pt=37.620070,55.753630,pmwtm1~37.64,55.76363,pmwtm99&apikey=85950243-e5f2-488a-8ecc-1cd21cd181e2')
    with open("static/img/img.jpg", "wb") as out:
        out.write(pic.content)

    place = session.query(Place).filter_by(name=adress).first()
    if not place:
        place = Place(name=adress)
        session.add(place)
        session.commit()

    if request.method == 'POST':
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        if comment:
            new_comment = Comment(text=comment, place_id=place.id)
            session.add(new_comment)
            session.commit()
        if rating:
            rating = int(rating)
            place.num_ratings += 1
            place.rating = ((place.rating * (place.num_ratings - 1)) + rating) / place.num_ratings
            session.commit()
        return redirect(url_for('show_sbor', adress=adress))
    
    comments = session.query(Comment).filter_by(place_id=place.id).all()
    return render_template('show_sbor.html', data=data, comments=comments, rating=place.rating, num_ratings=place.num_ratings)


@app.route('/add_place', methods=['GET', 'POST'])
def add_place():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        phones = request.form.get('phones')
        hours = request.form.get('hours')

        if name and description:
            place = Place(
                name=name,
                description=description,
                phones=phones,
                hours=hours
            )
            session.add(place)
            session.commit()
            return redirect(url_for('index'))

    return render_template('add_place.html')


@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        new_event = Event(title=title, description=description, date=date, location=location)
        session.add(new_event)
        session.commit()
        return redirect(url_for('events'))
    events = session.query(Event).all()
    return render_template('events.html', events=events)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
