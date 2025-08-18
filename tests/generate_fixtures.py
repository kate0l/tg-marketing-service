from typing import List, Dict, Any
from itertools import islice

from tests.data_generator import DataGenerator, NUM_OF_FIXTURES, ROLE_MAXLENGTH, BIO_MAXLENGTH


class ModelAndFormFixtureGenerator:
    """
    Builds model and form payload fixtures using only DataGenerator.
    Assumptions:
      - FK fields are represented as integer IDs (placeholders).
      - M2M fields are represented as lists of integer IDs.
      - save_fixture writes {"valid": [...], "invalid": [...]} JSON files.
    """
    def __init__(self, num: int = NUM_OF_FIXTURES) -> None:
        self.gen = DataGenerator(num)
        # convenience shorthands
        self.rules = self.gen.rules

    @staticmethod
    def _min_len(*seqs) -> int:
        return min(len(s) for s in seqs if hasattr(s, '__len__') and len(s) is not None) if seqs else 0

    def _save(self, name: str, valid: List[Dict[str, Any]]) -> None:
        # Build shape-consistent invalid payloads
        def _invalid_like(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            bad = []
            for row in rows or []:
                wrong = {}
                for k, v in row.items():
                    if k == "channels":
                        wrong[k] = []  # violates M2M min selection
                    elif k.endswith("_id") or k in {"participants_count", "daily_growth", "average_views", "order", "limit"}:
                        wrong[k] = "NaN"  # wrong type for ints/IDs
                    elif "email" in k:
                        wrong[k] = "invalid@"
                    elif "url" in k:
                        wrong[k] = "http:/bad"
                    elif "date" in k or "parsed_at" in k or "created_at" in k:
                        wrong[k] = "not-a-date"
                    elif isinstance(v, bool) or k.startswith("is_") or k.startswith("can_"):
                        wrong[k] = "true"  # wrong type for booleans
                    else:
                        wrong[k] = ""  # empty string for required text
                bad.append(wrong)
            return bad[: self.gen.data_size]
        self.gen.save_fixture(name, valid, _invalid_like(valid))
    # ---------- Model fixtures ----------
    def users_user(self) -> None:
        # username, first_name, last_name: short text without leading/trailing whitespace
        usernames = self.gen.generate_text(self.rules['unlimited']['text'], max_len=30, remove_whitespace=True, ensure_unique=True)
        first_names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        last_names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        emails = self.gen.generate_emails(self.rules['limited']['email'])
        bios = self.gen.generate_text(self.rules['unlimited']['text'], max_len=BIO_MAXLENGTH)
        roles = self.gen.generate_text(self.rules['unlimited']['text'], max_len=ROLE_MAXLENGTH, remove_whitespace=True)
        avatars = self.gen.generate_urls(self.rules['limited']['url'])

        n = self._min_len(usernames, first_names, last_names, emails, bios, roles, avatars)
        valid = []
        for i in range(n):
            valid.append({
                "username": usernames[i],
                "first_name": first_names[i],
                "last_name": last_names[i],
                "email": emails[i],
                "bio": bios[i],
                "role": roles[i],
                "avatar_image": avatars[i],
                # Other AbstractUser fields may be set by defaults when actually saved to DB.
            })
        self._save("model_users__User", valid)

    def users_partnerprofile(self) -> None:
        # user_id placeholders
        user_ids = self.gen.generate_int(self.rules['unlimited']['int'], max_len=3, ensure_unique=True)
        # status choices mapped via ints
        statuses = ['active', 'pending', 'rejected', 'suspended']
        status_idxs = self.gen.generate_int(self.rules['unlimited']['int'], max_len=2)
        # partner_since datetime strings
        partner_since = self.gen.generate_datetime(self.rules['limited']['datetime'])
        # balance as decimal-like string built from integers
        cents = self.gen.generate_int(self.rules['unlimited']['int'], max_len=5)
        payment_details = self.gen.generate_text(self.rules['unlimited']['text'], max_len=120)
        partner_codes = self.gen.generate_text(self.rules['unlimited']['text'], max_len=30, remove_whitespace=True, ensure_unique=True)

        n = self._min_len(user_ids, status_idxs, partner_since, cents, payment_details, partner_codes)
        valid = []
        for i in range(n):
            valid.append({
                "user_id": user_ids[i],
                "status": statuses[status_idxs[i] % len(statuses)],
                "partner_since": partner_since[i],
                "balance": f"{cents[i] / 100:.2f}",
                "payment_details": payment_details[i],
                "partner_code": partner_codes[i],
            })
        self._save("model_users__PartnerProfile", valid)

    def parser_telegramchannel(self) -> None:
        channel_ids = self.gen.generate_int(self.rules['unlimited']['int'], max_len=12, ensure_unique=True)
        usernames = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        titles = self.gen.generate_text(self.rules['unlimited']['text'], max_len=50, remove_whitespace=True)
        descriptions = self.gen.generate_text(self.rules['unlimited']['text'], max_len=200)
        participants = self.gen.generate_int(self.rules['unlimited']['int'], max_len=7)
        pinned = self.gen.generate_json_object()
        creation_dates = self.gen.generate_datetime(self.rules['limited']['datetime'])
        last_messages = self.gen.generate_json_object()
        average_views = self.gen.generate_int(self.rules['unlimited']['int'], max_len=7)
        parsed_at = self.gen.generate_datetime(self.rules['limited']['datetime'])
        n = self._min_len(channel_ids, usernames, titles, descriptions, participants, pinned, creation_dates, last_messages, average_views, parsed_at)
        valid = []
        for i in range(n):
            valid.append({
                "channel_id": channel_ids[i],
                "username": usernames[i],
                "title": titles[i],
                "description": descriptions[i],
                "participants_count": participants[i],
                "pinned_messages": pinned[i],
                "creation_date": creation_dates[i],
                "last_messages": last_messages[i],
                "average_views": average_views[i],
                "parsed_at": parsed_at[i],
            })
        self._save("model_parser__TelegramChannel", valid)

    def parser_channelmoderator(self) -> None:
        user_ids = self.gen.generate_int(self.rules['unlimited']['int'], max_len=3)
        channel_ids = self.gen.generate_int(self.rules['unlimited']['int'], max_len=3)
        flags = self.gen.generate_int(self.rules['unlimited']['int'], max_len=1)
        flags2 = self.gen.generate_int(self.rules['unlimited']['int'], max_len=1)
        flags3 = self.gen.generate_int(self.rules['unlimited']['int'], max_len=1)
        parsed_at = self.gen.generate_datetime(self.rules['limited']['datetime'])
        n = min(len(user_ids), len(channel_ids), len(flags), len(flags2), len(flags3), len(parsed_at))

        seen_pairs = set()
        valid = []
        for i in range(n):
            pair = (user_ids[i], channel_ids[i])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            valid.append({
                "user_id": user_ids[i],
                "channel_id": channel_ids[i],
                "is_owner": bool(flags[i] % 2),
                "can_edit": bool(flags2[i] % 2),
                "can_delete": bool(flags3[i] % 2),
                "can_manage_moderators": bool((flags[i] + flags2[i]) % 2),
                "created_at": parsed_at[i],
            })
        self._save("model_parser__ChannelModerator", valid)

    def parser_channelstats(self) -> None:
        channel_ids = self.gen.generate_int(self.rules['unlimited']['int'], max_len=4)
        participants = self.gen.generate_int(self.rules['unlimited']['int'], max_len=7)
        daily_growth = self.gen.generate_int(self.rules['unlimited']['int'], max_len=5)
        parsed_at = self.gen.generate_datetime(self.rules['limited']['datetime'])

        n = self._min_len(channel_ids, participants, daily_growth, parsed_at)
        valid = []
        for i in range(n):
            valid.append({
                "channel_id": channel_ids[i],
                "participants_count": participants[i],
                "daily_growth": daily_growth[i],
                "parsed_at": parsed_at[i],
            })
        self._save("model_parser__ChannelStats", valid)

    def group_channels_group(self) -> None:
        names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=50, remove_whitespace=True, ensure_unique=True)
        descriptions = self.gen.generate_text(self.rules['unlimited']['text'], max_len=200)
        owner_ids = self.gen.generate_int(self.rules['unlimited']['int'], max_len=3)
        flags = self.gen.generate_int(self.rules['unlimited']['int'], max_len=1)
        orders = self.gen.generate_int(self.rules['unlimited']['int'], max_len=2)
        image_urls = self.gen.generate_urls(self.rules['limited']['url'])
        created = self.gen.generate_datetime(self.rules['limited']['datetime'])
        n = self._min_len(names, descriptions, owner_ids, flags, orders, image_urls, created)

        def chunked(iterable, size):
            it = iter(iterable)
            while True:
                chunk = list(islice(it, size))
                if not chunk:
                    break
                yield chunk

        # Ensure enough for n groups
        channels_lists = list(chunked(list(m2m_pool) * 3, 3))  # replicate pool to get enough chunks
        if len(channels_lists) < n:
            channels_lists.extend(channels_lists[:n - len(channels_lists)])

        def _slugify(text: str) -> str:
            s = ''.join(ch.lower() if ch.isalnum() else '-' for ch in text).strip('-')
            while '--' in s:
                s = s.replace('--', '-')
            return s[:60]  # model max_length

        valid = []
        for i in range(n):
            name_i = names[i]
            valid.append({
                "name": name_i,
                "slug": _slugify(name_i),
                "description": descriptions[i],
                "owner_id": owner_ids[i],
                "is_editorial": bool(flags[i] % 2),
                "order": orders[i],
                "channels": channels_lists[i],
                "image_url": image_urls[i],
                "created_at": created[i],
            })
        self._save("model_group_channels__Group", valid)

    # ---------- Form fixtures ----------

    def form_users_userlogin(self) -> None:
        usernames = self.gen.generate_text(self.rules['unlimited']['text'], max_len=30, remove_whitespace=True)
        passwords = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        n = self._min_len(usernames, passwords)
        valid = [{"username": usernames[i], "password": passwords[i]} for i in range(n)]
        self._save("form_users__UserLoginForm", valid)

    def form_users_userreg(self) -> None:
        first_names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        last_names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        usernames = self.gen.generate_text(self.rules['unlimited']['text'], max_len=30, remove_whitespace=True)
        emails = self.gen.generate_emails(self.rules['limited']['email'])
        bios = self.gen.generate_text(self.rules['unlimited']['text'], max_len=BIO_MAXLENGTH)
        avatars = self.gen.generate_urls(self.rules['limited']['url'])
        passwords = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)

        n = min(map(len, [first_names, last_names, usernames, emails, bios, avatars, passwords]))
        valid = []
        for i in range(n):
            pwd = passwords[i]
            valid.append({
                "first_name": first_names[i],
                "last_name": last_names[i],
                "username": usernames[i],
                "email": emails[i],
                "bio": bios[i],
                "avatar_image": avatars[i],
                "password1": pwd,
                "password2": pwd,
                "terms": True,
            })
        self._save("form_users__UserRegForm", valid)

    def form_users_userupdate(self) -> None:
        first_names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        last_names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        usernames = self.gen.generate_text(self.rules['unlimited']['text'], max_len=30, remove_whitespace=True)
        emails = self.gen.generate_emails(self.rules['limited']['email'])
        bios = self.gen.generate_text(self.rules['unlimited']['text'], max_len=BIO_MAXLENGTH)
        avatars = self.gen.generate_urls(self.rules['limited']['url'])
        passwords = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)

        n = min(map(len, [first_names, last_names, usernames, emails, bios, avatars, passwords]))
        valid = []
        for i in range(n):
            pwd = passwords[i]
            valid.append({
                "first_name": first_names[i],
                "last_name": last_names[i],
                "username": usernames[i],
                "email": emails[i],
                "bio": bios[i],
                "avatar_image": avatars[i],
                "password1": pwd,
                "password2": pwd,
            })
        self._save("form_users__UserUpdateForm", valid)

    def form_users_avatarchange(self) -> None:
        avatars = self.gen.generate_urls(self.rules['limited']['url'])
        valid = [{"avatar_image": u} for u in avatars]
        self._save("form_users__AvatarChange", valid)

    def form_users_restore_password_request(self) -> None:
        emails = self.gen.generate_emails(self.rules['limited']['email'])
        valid = [{"email": e} for e in emails]
        self._save("form_users__RestorePasswordRequestForm", valid)

    def form_users_restore_password(self) -> None:
        passwords = self.gen.generate_text(self.rules['unlimited']['text'], max_len=20, remove_whitespace=True)
        n = len(passwords)
        valid = [{"new_password1": passwords[i], "new_password2": passwords[i]} for i in range(n)]
        self._save("form_users__RestorePasswordForm", valid)

    def form_parser_channelparse(self) -> None:
        identifiers = self.gen.generate_text(self.rules['unlimited']['text'], max_len=50, remove_whitespace=True)
        limits = self.gen.generate_int(self.rules['unlimited']['int'], max_len=2)
        n = min(len(identifiers), len(limits))
        valid = [{"channel_identifier": identifiers[i], "limit": min(max(limits[i], 1), 20)} for i in range(n)]
        self._save("form_parser__ChannelParseForm", valid)

    def form_group_channels_creategroup(self) -> None:
        # Use model's stricter limits (name <= 50, description <= 200)
        names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=50, remove_whitespace=True)
        descriptions = self.gen.generate_text(self.rules['unlimited']['text'], max_len=200)
        images = self.gen.generate_urls(self.rules['limited']['url'])
        n = self._min_len(names, descriptions, images)
        valid = [{"name": names[i], "description": descriptions[i], "image_url": images[i]} for i in range(n)]
        self._save("form_group_channels__CreateGroupForm", valid)

    def form_group_channels_updategroup(self) -> None:
        names = self.gen.generate_text(self.rules['unlimited']['text'], max_len=50, remove_whitespace=True)
        descriptions = self.gen.generate_text(self.rules['unlimited']['text'], max_len=200)
        images = self.gen.generate_urls(self.rules['limited']['url'])
        n = self._min_len(names, descriptions, images)
        valid = [{"name": names[i], "description": descriptions[i], "image_url": images[i]} for i in range(n)]
        self._save("form_group_channels__UpdateGroupForm", valid)

    def form_group_channels_addchannel(self) -> None:
        # Produce 3 channel IDs per entry
        pool = list(self.gen.generate_int(self.rules['unlimited']['int'], max_len=3))
        if not pool:
            self._save("form_group_channels__AddChannelForm", [])
            return
        triples = []
        i = 0
        while len(triples) < self.gen.data_size:
            triples.append(pool[i % len(pool): (i % len(pool)) + 3] or pool[:3])
            i += 3
        valid = [{"channels": t} for t in triples]
        self._save("form_group_channels__AddChannelForm", valid)

    def generate_all(self) -> None:
        # Models
        self.users_user()
        self.users_partnerprofile()
        self.parser_telegramchannel()
        self.parser_channelmoderator()
        self.parser_channelstats()
        self.group_channels_group()
        # Forms
        self.form_users_userlogin()
        self.form_users_userreg()
        self.form_users_userupdate()
        self.form_users_avatarchange()
        self.form_users_restore_password_request()
        self.form_users_restore_password()
        self.form_parser_channelparse()
        self.form_group_channels_creategroup()
        self.form_group_channels_updategroup()
        self.form_group_channels_addchannel()


if __name__ == "__main__":
    ModelAndFormFixtureGenerator(NUM_OF_FIXTURES).generate_all()