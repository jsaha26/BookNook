from flask_restful import Resource, Api
from app import app
from models import db, Section

api = Api(app)

class SectionResource(Resource):
    def get(self):
        sections = Section.query.all()
        return {
            'sections': [{
                'id': section.id,
                'name': section.name,
                'date_created': section.date_created.strftime('%Y-%m-%d'),  # Format date as string
                'description': section.description,
                'image': section.image
            } for section in sections]
        }

api.add_resource(SectionResource, '/api/section')