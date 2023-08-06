from logilab.common.decorators import monkeypatch
from cubes.vcsfile import entities as vcsfile
from cubes.vcreview import entities as vcsreview

@monkeypatch(vcsfile.Repository, 'project')
@property
def project(self):
    if self.reverse_source_repository:
        return self.reverse_source_repository[0]
    return None

class PatchReviewBehaviour(vcsreview.PatchReviewBehaviour):
    """Select a reviewer for a patch.
    Try first to filter cwusers to ones that are already reviewers of
    a patch related to the same ticket. If the filter returns an empty
    set we fallback to the previous pre-selection.
    """
    def reviewers_rset(self):
        rset = self._cw.execute(
            'DISTINCT Any U '
            'WHERE P eid %(p)s, '
            '      P patch_ticket T, '
            '      PS patch_ticket T, '
            '      PS patch_reviewer U',
            {'p': self.entity.eid})
        if not rset:
            rset = super(PatchReviewBehaviour, self).reviewers_rset()
        return rset

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, butclasses=(PatchReviewBehaviour,))
    vreg.register_and_replace(PatchReviewBehaviour, vcsreview.PatchReviewBehaviour)
