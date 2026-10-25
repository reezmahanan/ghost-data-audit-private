import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Identity Resolution
users = list(csv.DictReader(open('dataset/user_identities.csv', encoding='utf-8')))
user_audit = list(csv.DictReader(open('dataset/user_audit_log.csv', encoding='utf-8')))

user_profiles = {} # uid -> dict of identifiers
email_to_uid = {}
phone_to_uid = {}
name_to_uid = {}

for u in users:
    uid = u['user_id']
    profile = {
        'user_id': uid,
        'emails': {u['email'].lower()},
        'phones': {u['phone']},
        'names': {u['name']},
        'hashes': {u['email_hash']}
    }
    email_to_uid[u['email'].lower()] = uid
    if u['phone']:
        phone_to_uid[u['phone']] = uid
    if u['name']:
        name_to_uid[u['name'].lower()] = uid
    user_profiles[uid] = profile

for a in user_audit:
    uid = a['user_id']
    if uid not in user_profiles:
        user_profiles[uid] = {'user_id': uid, 'emails': set(), 'phones': set(), 'names': set(), 'hashes': set()}
    field = a['field_name']
    old_v = a['old_value']
    new_v = a['new_value']
    if field == 'email':
        if old_v:
            user_profiles[uid]['emails'].add(old_v.lower())
            email_to_uid[old_v.lower()] = uid
        if new_v:
            user_profiles[uid]['emails'].add(new_v.lower())
            email_to_uid[new_v.lower()] = uid
    elif field == 'phone':
        if old_v: user_profiles[uid]['phones'].add(old_v)
        if new_v: user_profiles[uid]['phones'].add(new_v)
    elif field == 'name':
        if old_v: user_profiles[uid]['names'].add(old_v)
        if new_v: user_profiles[uid]['names'].add(new_v)

print(f"Indexed {len(user_profiles)} user profiles.")
