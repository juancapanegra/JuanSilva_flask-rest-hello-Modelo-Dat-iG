from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Text, Enum, JSON, Float
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()


class TypeEnum(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(
        String(15), nullable=False)
    lastname: Mapped[str] = mapped_column(
        String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    # 1 : N / Usuario: muchos posts
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="user")

    # 1 : N / Usuario: muchos comentarios
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="author")

    # 1 : N / Usuario: muchos medias
    medias: Mapped[List["Media"]] = relationship(
        "Media", back_populates="user")

    # 1 : N / Usuario:  Seguir a muchos
    following: Mapped[List["Follower"]] = relationship(
        "Follower",
        foreign_keys="Follower.user_from_id",
        back_populates="follower_user"
    )

    # 1 : N / Usuario: seguido por muchos
    followers: Mapped[List["Follower"]] = relationship(
        "Follower",
        foreign_keys="Follower.user_to_id",
        back_populates="followed_user"
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email
        }


class Media(db.Model):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[TypeEnum] = mapped_column(
        Enum(TypeEnum, name="type_enum", create_type=True),
        default=TypeEnum.IMAGE
    )
    url: Mapped[str] = mapped_column(String(80), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id')

    post: Mapped["Post"] = relationship(
        "Post", back_populates="medias")
    user: Mapped["User"] = relationship(
        "User", back_populates="medias")

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type.value if self.type else None,
            "url": self.url,
            "post_id": self.post_id
        }


class Post(db.Model):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    # Post: un usuario
    user: Mapped["User"] = relationship(
        "User", back_populates="posts")

    # Post: muchos comentarios
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="post")

    # Post: muchos medias
    medias: Mapped[List["Media"]] = relationship(
        "Media", back_populates="post")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id
        }


class Comment(db.Model):
    __tablename__ = 'comment'
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'))

    # Comentario: un autor/usuario
    author: Mapped["User"] = relationship(
        "User", back_populates="comments")

    # Comentario: un post
    post: Mapped["Post"] = relationship(
        "Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }


class Follower(db.Model):
    __tablename__ = 'follower'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_from_id: Mapped[int] = mapped_column(ForeignKey('user.id'))  # Seguir
    user_to_id: Mapped[int] = mapped_column(ForeignKey('user.id'))    # Seguido

    # Usuario que sigue a otro
    follower_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_from_id],
        back_populates="following"
    )

    # Usuario que es seguido
    followed_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_to_id],
        back_populates="followers"
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id
        }
