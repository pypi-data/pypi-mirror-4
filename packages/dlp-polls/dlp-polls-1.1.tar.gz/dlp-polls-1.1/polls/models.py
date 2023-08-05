from django.db import models


class Poll(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    class Meta:
        verbose_name = ('Poll')
        verbose_name_plural = ('Polls')

    def __unicode__(self):
        return self.name

    def get_questions_from_page(self, page_index):
        return self.page_set.all()[page_index].question_set.all()


class PollResultCategory(models.Model):
    from_score = models.IntegerField()
    to_score = models.IntegerField()
    text = models.CharField(max_length=200)
    poll = models.ForeignKey(Poll)

    class Meta:
        verbose_name = ('Results Category')
        verbose_name_plural = ('Results Categories')

    def __unicode__(self):
        return u"from %i to %i: %s" % (self.from_score, self.to_score, self.text)


class Page(models.Model):
    page_number = models.IntegerField()
    poll = models.ForeignKey(Poll)

    class Meta:
        verbose_name = ('Page')
        verbose_name_plural = ('Pages')

    def __unicode__(self):
        return u"t:%s p:%i" % (self.poll.name, self.page_number)


class Question(models.Model):
    text = models.CharField(max_length=200)
    page = models.ForeignKey(Page)

    class Meta:
        verbose_name = ('Question')
        verbose_name_plural = ('Questions')

    def __unicode__(self):
        return "t:%s p:%i: q:%s" % (self.page.poll.name[:10], self.page.page_number, self.text[:10])


class Answer(models.Model):
    text = models.CharField(max_length=200)
    score = models.IntegerField()
    question = models.ForeignKey(Question)

    class Meta:
        verbose_name = ('Answer')
        verbose_name_plural = ('Answers')

    def __unicode__(self):
        return u"t:%s p:%i q:%s a:%s s:%i" % (self.question.page.poll.name[:10],
            self.question.page.page_number,
            self.question.text[:10],
            self.text[:10],
            self.score)