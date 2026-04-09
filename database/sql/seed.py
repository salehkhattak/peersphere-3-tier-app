"""Seed script to populate the database with sample data."""
from app import db, bcrypt
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.community import Community, CommunityMember
from app.models.post import Post, Comment, Like
from app.models.event import Event, EventAttendee
from app.models.mentor import Mentor
from app.models.activity import ActivityLog
from app.models.notification import Notification
from datetime import datetime, timedelta
import random


def seed_database():
    """Seed the database with sample data."""
    print("🌱 Seeding database...")

    # ----- Skills -----
    skill_names = [
        'Python', 'JavaScript', 'Machine Learning', 'Cloud Computing',
        'Data Science', 'Web Development', 'Photography', 'Marketing',
        'UI/UX Design', 'Blockchain', 'Cybersecurity', 'Mobile Development',
        'DevOps', 'Tourism', 'Public Speaking', 'Project Management',
        'Artificial Intelligence', 'Deep Learning', 'React', 'Node.js'
    ]
    skills = []
    for name in skill_names:
        s = Skill(skill_name=name)
        db.session.add(s)
        skills.append(s)
    db.session.commit()
    print(f"  ✅ {len(skills)} skills created")

    # ----- Users -----
    pw_hash = bcrypt.generate_password_hash('password123').decode('utf-8')

    users_data = [
        {'name': 'Ahmed Khan', 'email': 'ahmed@uni.edu', 'role': 'student', 'university': 'National University', 'department': 'Computer Science', 'graduation_year': 2026, 'bio': 'Passionate about AI and web development. Love building things that make a difference.'},
        {'name': 'Sara Ali', 'email': 'sara@uni.edu', 'role': 'student', 'university': 'National University', 'department': 'Computer Science', 'graduation_year': 2025, 'bio': 'Full-stack developer & open source enthusiast. Always learning something new!'},
        {'name': 'Dr. Rashid Mahmood', 'email': 'rashid@uni.edu', 'role': 'alumni', 'university': 'National University', 'department': 'Computer Science', 'graduation_year': 2018, 'bio': 'Senior Software Engineer at Google. Passionate about mentoring the next generation.'},
        {'name': 'Maria Hassan', 'email': 'maria@uni.edu', 'role': 'student', 'university': 'National University', 'department': 'Business Admin', 'graduation_year': 2026, 'bio': 'Marketing enthusiast with a love for creative campaigns and brand storytelling.'},
        {'name': 'Usman Tariq', 'email': 'usman@uni.edu', 'role': 'student', 'university': 'National University', 'department': 'Electrical Engineering', 'graduation_year': 2025, 'bio': 'IoT and embedded systems tinkerer. Building the future one circuit at a time.'},
        {'name': 'Fatima Zahra', 'email': 'fatima@uni.edu', 'role': 'alumni', 'university': 'National University', 'department': 'Data Science', 'graduation_year': 2020, 'bio': 'Data Scientist at Microsoft. Passionate about transforming data into insights.'},
        {'name': 'Admin User', 'email': 'admin@peersphere.com', 'role': 'admin', 'university': 'National University', 'department': 'Administration', 'graduation_year': None, 'bio': 'PeerSphere platform administrator.'},
        {'name': 'Hassan Raza', 'email': 'hassan@uni.edu', 'role': 'student', 'university': 'National University', 'department': 'Computer Science', 'graduation_year': 2027, 'bio': 'Freshman exploring the world of cloud computing and machine learning.'},
        {'name': 'Ayesha Siddiqui', 'email': 'ayesha@uni.edu', 'role': 'student', 'university': 'City University', 'department': 'Computer Science', 'graduation_year': 2026, 'bio': 'Cybersecurity researcher and CTF player. Securing the digital world.'},
        {'name': 'Bilal Ahmed', 'email': 'bilal@uni.edu', 'role': 'alumni', 'university': 'City University', 'department': 'Software Engineering', 'graduation_year': 2019, 'bio': 'CTO at a fintech startup. Building scalable solutions for millions.'},
    ]

    users = []
    for data in users_data:
        u = User(password_hash=pw_hash, **data)
        db.session.add(u)
        users.append(u)
    db.session.commit()
    print(f"  ✅ {len(users)} users created")

    # ----- Assign Skills -----
    for user in users:
        num_skills = random.randint(2, 6)
        chosen = random.sample(skills, num_skills)
        for skill in chosen:
            us = UserSkill(user_id=user.id, skill_id=skill.id)
            db.session.add(us)
    db.session.commit()
    print("  ✅ Skills assigned to users")

    # ----- Communities -----
    communities_data = [
        {'name': 'Cloud Computing Club', 'description': 'Exploring the latest in cloud technology, AWS, Azure, and GCP. Join us for workshops and study groups!', 'created_by': users[0].id},
        {'name': 'AI/ML Students', 'description': 'A community for AI and machine learning enthusiasts. Share papers, projects, and collaborate!', 'created_by': users[1].id},
        {'name': 'Tourism Society', 'description': 'Discover amazing travel destinations, plan group trips, and share your travel stories.', 'created_by': users[3].id},
        {'name': 'Startup Founders', 'description': 'Connect with aspiring entrepreneurs, share ideas, find co-founders, and build the next big thing!', 'created_by': users[2].id},
        {'name': 'Photography Club', 'description': 'Capture beautiful moments! Share your photography, get feedback, and learn new techniques.', 'created_by': users[4].id},
        {'name': 'Cybersecurity Guild', 'description': 'Ethical hacking, CTFs, security research, and best practices. Stay secure!', 'created_by': users[8].id},
        {'name': 'Web Dev Hub', 'description': 'Everything web development — React, Node, Flask, Django, and more. Build, learn, share.', 'created_by': users[1].id},
        {'name': 'Data Science Circle', 'description': 'From EDA to deep learning pipelines. Let us explore data together.', 'created_by': users[5].id},
    ]

    communities = []
    for data in communities_data:
        c = Community(**data)
        db.session.add(c)
        communities.append(c)
    db.session.commit()

    print(f"  ✅ {len(communities)} communities created")

    # ----- Posts -----
    post_contents = [
        "Just finished building my first machine learning model! 🤖 The accuracy is 94% on the test set. Next step: deploying it to the cloud.",
        "Looking for team members for the upcoming hackathon! We need a frontend developer and a UI/UX designer. Who's interested? 🚀",
        "Great workshop on React hooks today! Here are my key takeaways and a link to the code samples we worked through.",
        "Sharing my notes on distributed systems from today's lecture. Chapter 5 was particularly interesting — CAP theorem explained beautifully!",
        "Starting a study group for cloud computing certification (AWS Solutions Architect). Drop a comment if you want to join! ☁️",
        "This semester's project is going to be epic. Building a real-time chat application with WebSockets and Node.js! 💬",
        "Photography tip: Golden hour light + leading lines = stunning compositions. Here's a shot I took at campus today. 📸",
        "Just got accepted into Google's Summer of Code! So excited to contribute to open source this summer! 🎉",
        "Data Science insight: Always start with EDA before jumping into model building. You'd be surprised what you find in the data!",
        "The startup pitch competition is next week. Who else is participating? Let's connect and practice our pitches together.",
        "Cybersecurity alert: Always use 2FA on your university accounts. Here's a quick guide on setting it up properly. 🔐",
        "Amazing networking event today! Met so many talented people. The power of community is incredible. ❤️",
    ]

    posts = []
    for i, content in enumerate(post_contents):
        user = users[i % len(users)]
        community = random.choice(communities) if random.random() > 0.4 else None
        post = Post(
            user_id=user.id,
            content=content,
            community_id=community.id if community else None,
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 168))
        )
        db.session.add(post)
        posts.append(post)
    db.session.commit()

    # Add likes and comments
    for post in posts:
        like_count = random.randint(1, 5)
        for u in random.sample(users, like_count):
            like = Like(user_id=u.id, post_id=post.id)
            db.session.add(like)

    comment_texts = [
        "This is amazing! Great work! 👏",
        "I'd love to join! Count me in!",
        "Really insightful, thanks for sharing!",
        "Can you share the resources link?",
        "Congrats! Well deserved! 🎉",
        "This is super helpful, bookmarked!",
        "Impressive work, keep it up!",
    ]
    for post in posts:
        comment_count = random.randint(0, 3)
        for _ in range(comment_count):
            comment = Comment(
                user_id=random.choice(users).id,
                post_id=post.id,
                comment_text=random.choice(comment_texts),
                created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 24))
            )
            db.session.add(comment)
    db.session.commit()
    print(f"  ✅ {len(posts)} posts with likes and comments created")

    # ----- Events -----
    events_data = [
        {'title': 'Annual Hackathon 2026', 'description': 'A 48-hour coding marathon! Build innovative solutions, win prizes, and have fun. Open to all students.', 'date': datetime.utcnow() + timedelta(days=14), 'location': 'Main Auditorium, Block A', 'event_type': 'hackathon', 'created_by': users[0].id},
        {'title': 'Cloud Computing Workshop', 'description': 'Hands-on workshop on AWS services. Learn EC2, S3, Lambda, and more. Bring your laptop!', 'date': datetime.utcnow() + timedelta(days=7), 'location': 'Lab 4, CS Building', 'event_type': 'workshop', 'created_by': users[2].id},
        {'title': 'AI Ethics Seminar', 'description': 'A deep dive into the ethical considerations of artificial intelligence with guest speakers from industry.', 'date': datetime.utcnow() + timedelta(days=21), 'location': 'Seminar Hall B', 'event_type': 'seminar', 'created_by': users[5].id},
        {'title': 'Networking Meetup', 'description': 'Casual networking session for students and alumni. Share experiences, make connections, and explore opportunities.', 'date': datetime.utcnow() + timedelta(days=5), 'location': 'University Cafe', 'event_type': 'meetup', 'created_by': users[3].id},
        {'title': 'Web Development Bootcamp', 'description': 'Intensive 3-day bootcamp covering HTML, CSS, JavaScript, React, and Node.js. Perfect for beginners!', 'date': datetime.utcnow() + timedelta(days=10), 'location': 'Online (Zoom)', 'event_type': 'workshop', 'created_by': users[1].id},
    ]

    events = []
    for data in events_data:
        e = Event(**data)
        db.session.add(e)
        events.append(e)
    db.session.commit()

    for event in events:
        attendee_count = random.randint(3, 7)
        for u in random.sample(users, attendee_count):
            existing = EventAttendee.query.filter_by(user_id=u.id, event_id=event.id).first()
            if not existing:
                ea = EventAttendee(user_id=u.id, event_id=event.id)
                db.session.add(ea)
    db.session.commit()
    print(f"  ✅ {len(events)} events created with attendees")

    # ----- Mentors -----
    mentor_data = [
        {'user_id': users[2].id, 'expertise': 'Software Engineering, System Design, Career Growth', 'availability': 'Weekends'},
        {'user_id': users[5].id, 'expertise': 'Data Science, Machine Learning, Python', 'availability': 'Flexible'},
        {'user_id': users[9].id, 'expertise': 'Startups, Product Management, Fintech', 'availability': 'Weekday evenings'},
    ]

    for data in mentor_data:
        m = Mentor(**data)
        db.session.add(m)
    db.session.commit()
    print("  ✅ Mentors registered")

    print("🎉 Database seeded successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        # Create all tables first
        db.create_all()
        seed_database()
