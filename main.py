import os
import fastapi
import uvicorn
import json
from dotenv import load_dotenv
from typing import Dict, List, Optional
from fastapi import Path, status
from fastapi.responses import JSONResponse
from models import NewsDetailResponse, Comment, ListNewsResponse, News

load_dotenv()

app = fastapi.FastAPI()

comments_by_news_id: Dict[int, List[Optional[Comment]]] = {}


def load_file(path: str) -> Dict:
    with open(path, encoding='utf-8') as file:
        return json.load(file)


def get_comments_by_news_id(news_id: int) -> List[Optional[Dict]]:
    return comments_by_news_id.get(news_id, [])


@app.on_event('startup')
async def pre_processing() -> None:
    '''
    Предобработка файла с комментариями.
    Формирует хеш-таблицу: ключ - id новости, значение - список из комментариев
    '''
    comments_data = load_file(os.getenv("COMMENTS_FILE"))
    for comment_dict in comments_data['comments']:
        news_id = comment_dict['news_id']
        if comments_by_news_id.get(news_id):
            comments_by_news_id[news_id].append(Comment(**comment_dict))
        else:
            comments_by_news_id[news_id] = [Comment(**comment_dict)]


@app.get('/', response_model=ListNewsResponse)
async def get_all_news():
    news_data = load_file(os.getenv("NEWS_FILE"))
    news_not_deleted: List[Optional[News]] = []
    for news_item in news_data['news']:
        if not news_item['deleted']:
            news_id = news_item['id']
            comments_count = len(get_comments_by_news_id(news_id=news_id))
            news_item['comments_count'] = comments_count
            news_not_deleted.append(News(**news_item))
    return {
        'news': news_not_deleted,
        'news_count': len(news_not_deleted)
    }


@app.get('/news/{id}', response_model=NewsDetailResponse)
async def get_news_by_id(id: int = Path(ge=1)):
    news_data = load_file(os.getenv("NEWS_FILE"))
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
