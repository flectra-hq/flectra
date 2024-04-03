# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.survey.controllers import main


class ApplicantSurvey(main.Survey):
    def _prepare_retry_additional_values(self, answer):
        result = super()._prepare_retry_additional_values(answer)
        if answer.applicant_id:
            result["applicant_id"] = answer.applicant_id.id

        return result
