import fastapi
import uvicorn
import json
from typing import Dict, List, Optional
from fastapi import Path, status, Depends
from fastapi.responses import JSONResponse
from models import NewsDetailResponse, Comment

app = fastapi.FastAPI()

comments_by_news_id: Dict[int, List[Optional[Comment]]] = {}


def load_file(path: str) -> Dict:
    with open(path, encoding='utf-8') as file:
        return json.load(file)


@app.on_event('startup')
async def pre_processing():
    '''
    Предобработка файла с комментариями.
    Формирует хеш-таблицу: ключ - id новости, значение - список из комментариев
    '''
    comments_data = load_file('comments.json')
    for comment_dict in comments_data['comments']:
        news_id = comment_dict['news_id']
        if comments_by_news_id.get(news_id):
            comments_by_news_id[news_id].append(Comment(**comment_dict))
        else:
            comments_by_news_id[news_id] = [Comment(**comment_dict)]


def get_comments_by_news_id(news_id: int) -> List[Optional[Dict]]:
    return comments_by_news_id[news_id]


def get_comments_count_by_id(news_id: int) -> int:
    with open('comments.json', encoding='utf-8') as file:
        comments_array = json.load(file).get('comments')
        comments_count = 0
        for comment_info in comments_array:
            if comment_info['news_id'] == news_id:
                comments_count += 1
        return comments_count


@app.get('/')
async def get_all_news():
    with open('news.json', encoding='utf-8') as file:
        news_data = json.load(file)

    news_count = len(news_data.get('news'))
    for i in range(news_count):
        if not news_data['news'][i]['deleted']:  ## возвращать необходимо не удаленные записи (поле "deleted")
            news_id = news_data['news'][i]['id']
            news_comments = get_comments_count_by_id(news_id)
            news_data['news'][i]['comments_count'] = news_comments

    return JSONResponse(content=news_data, status_code=status.HTTP_200_OK)


@app.get('/news/{id}', response_model=NewsDetailResponse)
async def get_news_by_id(id: int = Path(ge=1)):
    news_data = load_file('news.json')
    # если в массиве новости новости начинаются с id=1 и в порядке возрастания, иначе поиск циклом
    if len(news_data['news']) < id:
        return JSONResponse(content='No such news', status_code=status.HTTP_404_NOT_FOUND)
    news_by_id = news_data['news'][id - 1]
    if news_by_id['deleted']:
        return JSONResponse(content='The news was deleted', status_code=status.HTTP_404_NOT_FOUND)

    comments_by_news_id = get_comments_by_news_id(news_id=id)
    news_by_id['comments'] = comments_by_news_id
    news_by_id['comments_count'] = len(comments_by_news_id)
    return news_by_id


if __name__ == '__main__':
    uvicorn.run(app=app,
                host='127.0.0.1',
                port=8000,
                )
