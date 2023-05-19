import os
from typing import Union

from dotenv import load_dotenv
from app.moodle import moodle_api

load_dotenv()

moodle_api.URL = os.environ.get('MOODLE_URL')
moodle_api.KEY = os.environ.get('MOODLE_API_KEY')


class MoodleHelper:
    @classmethod
    def get_all_categories(cls):
        return moodle_api.call('core_course_get_categories',
                               criteria=[{'key': 'parent', 'value': 0}],
                               addsubcategories=0)

    @classmethod
    def get_all_courses(cls):
        return moodle_api.call('core_course_get_courses')

    @classmethod
    def get_quizzes_by_courses(cls, course_ids: Union[list[int], int]):
        if isinstance(course_ids, int):
            course_ids = [course_ids]
        return moodle_api.call('mod_quiz_get_quizzes_by_courses',  courseids=course_ids)

