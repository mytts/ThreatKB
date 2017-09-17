from app import app, db
from app.models import c2dns
from flask import abort, jsonify, request
from flask.ext.login import login_required, current_user
from dateutil import parser
from sqlalchemy import exc
import json

from app.routes.tags_mapping import create_tags_mapping, delete_tags_mapping


@app.route('/ThreatKB/c2dns', methods=['GET'])
@login_required
def get_all_c2dns():
    entities = c2dns.C2dns.query

    if not current_user.admin:
        entities = entities.filter_by(owner_user_id=current_user.id)

    entities = entities.all()

    return json.dumps([entity.to_dict() for entity in entities])


@app.route('/ThreatKB/c2dns/<int:id>', methods=['GET'])
def get_c2dns(id):
    entity = c2dns.C2dns.query.get(id)
    if not entity:
        abort(404)
    if not current_user.admin and entity.owner_user_id != current_user.id:
        abort(403)
    return jsonify(entity.to_dict())


@app.route('/ThreatKB/c2dns', methods=['POST'])
@login_required
def create_c2dns():
    entity = c2dns.C2dns(
        domain_name=request.json['domain_name']
        , match_type=request.json['match_type']
        , reference_link=request.json['reference_link']
        , reference_text=request.json['reference_text']
        , expiration_type=request.json['expiration_type']
        , expiration_timestamp=parser.parse(request.json['expiration_timestamp']) if request.json.get("expiration_type",
                                                                                                      None) else None
        , state=request.json['state']['state']
        , created_user_id=current_user.id
        , modified_user_id=current_user.id
    )
    db.session.add(entity)

    try:
        db.session.commit()
    except exc.IntegrityError:
        app.logger.error("Duplicate DNS: '%s'" % (entity.domain_name))
        abort(409)

    entity.tags = create_tags_mapping(entity.__tablename__, entity.id, request.json['tags'])

    return jsonify(entity.to_dict()), 201


@app.route('/ThreatKB/c2dns/<int:id>', methods=['PUT'])
@login_required
def update_c2dns(id):
    entity = c2dns.C2dns.query.get(id)
    if not entity:
        abort(404)
    if not current_user.admin and entity.owner_user_id != current_user.id:
        abort(403)
    entity = c2dns.C2dns(
        state=request.json['state']['state'] if request.json['state'] and 'state' in request.json['state'] else
        request.json['state'],
        domain_name=request.json['domain_name'],
        match_type=request.json['match_type'],
        reference_link=request.json['reference_link'],
        reference_text=request.json['reference_text'],
        expiration_type=request.json['expiration_type'],
        expiration_timestamp=parser.parse(request.json['expiration_timestamp']) if request.json.get(
            "expiration_timestamp", None) else None,
        id=id,
        owner_user_id=request.json['owner_user']['id'] if request.json.get("owner_user", None) and request.json[
            "owner_user"].get("id", None) else None,
        modified_user_id=current_user.id
    )
    db.session.merge(entity)

    try:
        db.session.commit()
    except exc.IntegrityError:
        app.logger.error("Duplicate DNS: '%s'" % (entity.domain_name))
        abort(409)

    create_tags_mapping(entity.__tablename__, entity.id, request.json['addedTags'])
    delete_tags_mapping(entity.__tablename__, entity.id, request.json['removedTags'])

    entity = c2dns.C2dns.query.get(entity.id)
    return jsonify(entity.to_dict()), 200


@app.route('/ThreatKB/c2dns/<int:id>', methods=['DELETE'])
@login_required
def delete_c2dns(id):
    entity = c2dns.C2dns.query.get(id)
    tag_mapping_to_delete = entity.to_dict()['tags']

    if not entity:
        abort(404)
    if not current_user.admin and entity.owner_user_id != current_user.id:
        abort(403)
    db.session.delete(entity)
    db.session.commit()

    delete_tags_mapping(entity.__tablename__, entity.id, tag_mapping_to_delete)

    return '', 204
